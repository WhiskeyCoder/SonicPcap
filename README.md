# PCAP Audio Transcriber

A tool to extract audio from PCAP files, transcribe the content, and store transcriptions in MongoDB.

```
 .oooooo..o                        o8o            ooooooooo.                                  
d8P'    `Y8                        `"'            `888   `Y88.                                
Y88bo.       .ooooo.  ooo. .oo.   oooo   .ooooo.   888   .d88'  .ooooo.   .oooo.   oo.ooooo.  
 `"Y8888o.  d88' `88b `888P"Y88b  `888  d88' `"Y8  888ooo88P'  d88' `"Y8 `P  )88b   888' `88b 
     `"Y88b 888   888  888   888   888  888        888         888        .oP"888   888   888 
oo     .d8P 888   888  888   888   888  888   .o8  888         888   .o8 d8(  888   888   888 
8""88888P'  `Y8bod8P' o888o o888o o888o `Y8bod8P' o888o        `Y8bod8P' `Y888""8o  888bod8P' 
                                                                                    888       
                                                                                   o888o      
```


## Overview

PCAP Audio Transcriber extracts RTP audio packets from network capture files, converts the raw audio data to a playable format, transcribes the spoken content using Google's Speech Recognition API, and stores the transcriptions in MongoDB for easy access and analysis.

Perfect for:
- Security researchers analyzing captured VoIP communications
- Forensic investigators extracting audio evidence from network traffic
- Network administrators monitoring voice quality and content

## Features

- **Audio Extraction**: Identifies and extracts RTP audio packets from PCAP files
- **Format Conversion**: Converts raw audio data to WAV format for transcription
- **Speech Recognition**: Transcribes audio using Google's Speech Recognition API
- **MongoDB Storage**: Stores transcriptions with metadata for easy querying
- **User-Friendly Interface**: Simple command-line menu system for all operations

## Installation

### Requirements

```bash
pip install speech_recognition
pip install pyshark
pip install pydub
pip install pymongo
```

### Dependencies

- **FFmpeg**: Required for audio conversion
- **MongoDB**: For storing transcriptions
- **Python 3.6+**: Required for all functionality

## Usage

Run the script:

```bash
python pcap_audio_transcriber.py
```

### Menu Options

1. **Process PCAP File**: Extract audio, transcribe, and store in MongoDB
2. **View Recent Transcriptions**: Display recent transcription entries
3. **Configure MongoDB Connection**: Update MongoDB connection settings
99. **Exit**: Quit the application

### Processing a PCAP File

1. Select option 1 from the menu
2. Enter the path to your PCAP file
3. Specify the packet filter (default: rtp)
4. Provide an output filename for the raw audio (optional)
5. The tool will:
   - Extract audio packets from the PCAP
   - Convert the raw audio to WAV format
   - Transcribe the audio
   - Store the transcription in MongoDB

## MongoDB Schema

Transcriptions are stored with the following structure:

```json
{
  "_id": ObjectId("..."),
  "transcription": "Transcribed text content...",
  "timestamp": ISODate("2023-06-15T14:23:11.000Z"),
  "metadata": {
    "source_pcap": "capture.pcap",
    "filter_type": "rtp",
    "raw_audio_file": "output.raw",
    "wav_file": "output.wav"
  }
}
```

## Troubleshooting

- **Connection Issues**: Ensure MongoDB is running and accessible
- **Transcription Errors**: Check that the audio extraction was successful and the format is compatible
- **PCAP Reading Problems**: Verify that your PCAP contains RTP packets
- **Check Logs**: Review `pcap_audio_transcriber.log` for detailed error information

## Advanced Usage

### Custom MongoDB Connection

Connect to a remote or authenticated MongoDB instance:

```
mongodb://username:password@hostname:port/database
```

### Processing Large PCAP Files

For large capture files, consider:
- Splitting the PCAP into smaller chunks
- Filtering for specific conversations
- Using display filters to target specific streams

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Thanks to wbwarnerb for help with the base audio extraction code
- Based on tools used for network traffic analysis and forensics
---

*Disclaimer: This tool should only be used on network traffic that you have permission to analyze. Capturing and analyzing network traffic without proper authorization may be illegal in your jurisdiction.*
