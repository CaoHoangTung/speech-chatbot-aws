import asyncio
import boto3
import pyaudio

SAMPLE_RATE = 16000
READ_CHUNK = 1024

# Create a Polly client
polly = boto3.client('polly',
    region_name="us-east-1"
)

class Speaker():
    def __init__(self):
        self.stopped = True
        pass

    def stop_speaking(self):
        self.stopped = True

    async def speak(self, text, voice_id="Ruth"):
        """
        Converts the given text to speech using Amazon Polly and returns the audio stream.
        
        Args:
            text (str): The text to be converted to speech.
            voice_id (str, optional): The ID of the voice to use for the speech synthesis. Defaults to 'Joanna'.
        
        Returns:
            bytes: The audio stream of the synthesized speech.
        """
        self.stopped = False
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='pcm',
            SampleRate=str(SAMPLE_RATE),
            VoiceId=voice_id,
            # TextType='ssml',
            Engine='generative'
        )
        
        audio_stream = response.get('AudioStream')

        # Play the audio stream
        p = pyaudio.PyAudio()
        output_stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True, 
                    frames_per_buffer=1024*4
                )
        while True:
            audio_data = audio_stream.read(READ_CHUNK)
            if not audio_data or self.stopped:
                break
            output_stream.write(audio_data)

        output_stream.stop_stream()
        output_stream.close()
        p.terminate()

        self.stop_speaking()

async def main():
    speaker = Speaker()
    text = "Hello! How are you doing? This is Polly from Amazon."
    # text = '<speak><amazon:domain name="news">I can also speak in a Newscaster style, as if I were reading a news article or delivering a flash briefing.</amazon:domain></speak>'
    await speaker.speak(text)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()