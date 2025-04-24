import speech_recognition as sr
from pydub import AudioSegment
import pyshark
import pymongo
import sys
import os
import logging
from datetime import datetime

banner = """
 .oooooo..o                        o8o            ooooooooo.                                  
d8P'    `Y8                        `"'            `888   `Y88.                                
Y88bo.       .ooooo.  ooo. .oo.   oooo   .ooooo.   888   .d88'  .ooooo.   .oooo.   oo.ooooo.  
 `"Y8888o.  d88' `88b `888P"Y88b  `888  d88' `"Y8  888ooo88P'  d88' `"Y8 `P  )88b   888' `88b 
     `"Y88b 888   888  888   888   888  888        888         888        .oP"888   888   888 
oo     .d8P 888   888  888   888   888  888   .o8  888         888   .o8 d8(  888   888   888 
8""88888P'  `Y8bod8P' o888o o888o o888o `Y8bod8P' o888o        `Y8bod8P' `Y888""8o  888bod8P' 
                                                                                    888       
                                                                                   o888o      
"""

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pcap_audio_transcriber.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PcapAudioTranscriber:
    def __init__(self, mongo_uri=None):
        """Initialize the PCAP Audio Transcriber with MongoDB connection."""
        self.mongo_client = None
        self.db = None
        
        # Connect to MongoDB if URI is provided
        if mongo_uri:
            self.connect_mongodb(mongo_uri)
        
    def connect_mongodb(self, mongo_uri):
        """Connect to MongoDB using the provided URI."""
        try:
            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.db = self.mongo_client.pcap_audio_db
            self.mongo_client.server_info()  # Will raise an exception if connection fails
            logger.info("Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def extract_audio_from_pcap(self, pcap_file, filter_type, out_file):
        """Extract audio packets from PCAP file."""
        try:
            rtp_list = []
            logger.info(f"Scraping: {pcap_file} with filter: {filter_type}")
            
            cap = pyshark.FileCapture(pcap_file, display_filter=filter_type)
            with open(out_file, 'wb') as raw_audio:
                for i in cap:
                    try:
                        rtp = i[3]  # RTP layer
                        if rtp.payload:
                            rtp_list.append(rtp.payload.split(":"))
                    except Exception as e:
                        pass  # Skip packets that don't match our filter
                
                for rtp_packet in rtp_list:
                    packet = " ".join(rtp_packet)
                    audio = bytearray.fromhex(packet)
                    raw_audio.write(audio)
            
            logger.info(f"Successfully extracted audio data to {out_file}")
            return out_file
        except Exception as e:
            logger.error(f"Error extracting audio from PCAP: {e}")
            return None
    
    def convert_to_wav(self, src_file, dst_file="output.wav"):
        """Convert the raw audio file to WAV format for transcription."""
        try:
            sound = AudioSegment.from_file(src_file, format="raw", 
                                          frame_rate=8000, channels=1, sample_width=2)
            sound.export(dst_file, format="wav")
            logger.info(f"Successfully converted audio to WAV format: {dst_file}")
            return dst_file
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            return None
    
    def transcribe_audio(self, audio_file):
        """Transcribe the audio file using speech recognition."""
        try:
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)  # Read the entire audio file
                transcription = r.recognize_google(audio)
                logger.info("Audio transcription successful")
                return transcription
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def save_transcription_to_mongodb(self, transcription, metadata=None):
        """Store the transcription in MongoDB."""
        if not self.db:
            logger.error("Not connected to MongoDB")
            return False
        
        try:
            collection = self.db.transcribed_audio
            
            # Prepare the document
            document = {
                "transcription": transcription,
                "timestamp": datetime.now(),
            }
            
            # Add metadata if provided
            if metadata:
                document["metadata"] = metadata
            
            # Insert into MongoDB
            result = collection.insert_one(document)
            logger.info(f"Transcription saved to MongoDB with ID: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving transcription to MongoDB: {e}")
            return False
    
    def process_pcap(self, pcap_file, filter_type="rtp", out_file=None):
        """Process a PCAP file: extract audio, convert to WAV, transcribe, and save to MongoDB."""
        # Generate output filename if not provided
        if not out_file:
            base_name = os.path.splitext(os.path.basename(pcap_file))[0]
            out_file = f"{base_name}_audio.raw"
        
        # Extract audio from PCAP
        raw_audio_file = self.extract_audio_from_pcap(pcap_file, filter_type, out_file)
        if not raw_audio_file:
            return False
        
        # Convert to WAV
        wav_file = self.convert_to_wav(raw_audio_file)
        if not wav_file:
            return False
        
        # Transcribe the audio
        transcription = self.transcribe_audio(wav_file)
        if not transcription:
            return False
        
        # Save to MongoDB
        metadata = {
            "source_pcap": pcap_file,
            "filter_type": filter_type,
            "raw_audio_file": raw_audio_file,
            "wav_file": wav_file
        }
        
        return self.save_transcription_to_mongodb(transcription, metadata)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main function to run the PCAP Audio Transcriber."""
    clear_screen()
        
    # Ask for MongoDB connection string
    mongo_uri = input("\nEnter MongoDB URI (default: mongodb://localhost:27017): ")
    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017"
    
    # Initialize the transcriber
    transcriber = PcapAudioTranscriber(mongo_uri)
    
    while True:
        clear_screen()
      
        print("\n#######################################################")
        print(banner)
        print("#######################################################")
        print("This tool will extract audio from PCAP files, transcribe it,")
        print("and save the transcription to MongoDB.")
        print("")
        print("1. Process PCAP File")
        print("2. View Recent Transcriptions")
        print("3. Configure MongoDB Connection")
        print("99. Exit")
        print("")
        
        choice = input("Choose an option from the list: ")
        
        if choice == "1":
            pcap_file = input("Enter the name of your pcap file: ")
            filter_type = input("What layer do you want to filter on? (default: rtp): ")
            if not filter_type:
                filter_type = "rtp"
            
            out_file = input("Provide your desired output filename (leave blank for auto-naming): ")
            
            if transcriber.process_pcap(pcap_file, filter_type, out_file):
                print("\nProcessing completed successfully!")
            else:
                print("\nProcessing failed. Check logs for details.")
            
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            if transcriber.db:
                collection = transcriber.db.transcribed_audio
                recent_docs = collection.find().sort("timestamp", -1).limit(5)
                
                print("\nRecent Transcriptions:")
                for doc in recent_docs:
                    print(f"\nID: {doc['_id']}")
                    print(f"Timestamp: {doc['timestamp']}")
                    print(f"Transcription: {doc['transcription']}")
                    if 'metadata' in doc:
                        print(f"Source PCAP: {doc['metadata']['source_pcap']}")
            else:
                print("\nNot connected to MongoDB.")
            
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            new_uri = input("\nEnter MongoDB URI: ")
            if new_uri:
                transcriber.connect_mongodb(new_uri)
            
            input("\nPress Enter to continue...")
        
        elif choice == "99":
            print("\nExiting the program. Goodbye!")
            break
        
        else:
            print("\nInvalid option. Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
