import asyncio
import time
import os
import boto3
import pyaudio

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
# from t2t_bedrock import converse
from t2t_agent import converse
from tts import Speaker

credentials = boto3.Session().get_credentials()

os.environ["AWS_ACCESS_KEY_ID"] = credentials.access_key
os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.secret_key
os.environ["AWS_SESSION_TOKEN"] = credentials.token

SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 1
CHANNEL_NUMS = 1
REGION = "ap-northeast-1"
BEDROCK_AGENT_REGION = "us-east-1"
CHUNK_SIZE = 1024 * 1

ONE_SECOND = 1
HALF_SECOND = .5

AGENT_ID = os.environ["AGENT_ID"]
AGENT_ALIAS_ID = os.environ["AGENT_ALIAS_ID"]

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, *args, audio_reader=None, **kwargs ):
        super().__init__(*args, **kwargs)
        # generate random session id
        self.session_id = str(time.time())
        self.audio_reader = audio_reader
        self.latest_transcribed_time = time.time()
        self.latest_transcribed_text = ""
        self.finished = False
        self.speaker = Speaker()

    def silent_detected(self):
        return time.time() - self.latest_transcribed_time > HALF_SECOND

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # if self.finished:
        #     return
        # print("handle_transcript_event")
        results = transcript_event.transcript.results
        print(results)

        # If the user speaks something, and the bot is speaking, stop and ask the user to say again
        if results and not self.speaker.stopped:
            self.speaker.speak("Sorry please go ahead")


        if not results and self.silent_detected() and self.latest_transcribed_text != "":
            latest_transcribed_text = self.latest_transcribed_text
            self.latest_transcribed_text = ""
            print("Finished")
            print(self.latest_transcribed_text)
            self.finished = True

            self.audio_reader.stop()
            print("Conversing", latest_transcribed_text)
            # text_response = converse(latest_transcribed_text)

            text_response = converse(
                agents_runtime_client = boto3.client('bedrock-agent-runtime', region_name=BEDROCK_AGENT_REGION),
                agent_id=AGENT_ID,
                agent_alias_id=AGENT_ALIAS_ID,
                session_id = self.session_id,
                prompt = latest_transcribed_text
            )
            print("Speaking", text_response)
            # Convert text to speech
            await self.speaker.speak(text_response)
            print("Spoken")
            return
        if results:
            transcribed_text = ""
            for alt in results[0].alternatives:
                transcribed_text += alt.transcript
            self.latest_transcribed_time = time.time()
            self.latest_transcribed_text = transcribed_text
        
        if not results:
            return

class AudioReader():
    def __init__(self):
        self.stopped = True

    def stop(self):
        self.stopped = True

    async def read_from_microphone(self, transcription_stream):
        self.stopped = False
        p = pyaudio.PyAudio()
        mic_stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

        while True:
            if self.stopped:
                break
            data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
            print("Sending audio event")
            await transcription_stream.input_stream.send_audio_event(data)
            print("Sent audio event")

        mic_stream.stop_stream()
        mic_stream.close()
        p.terminate()
        await transcription_stream.input_stream.end_stream()
        print("Stop read from microphone")
        self.stopped = True


async def basic_transcribe():
    # Setup up our client with our chosen AWS region
    audio_reader = AudioReader()

    while True:
        print("Start trans")
        client = TranscribeStreamingClient(region=REGION)

        # Start transcription to generate our async stream
        transcription_stream = await client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=SAMPLE_RATE,
            media_encoding="pcm",
        )

        # Instantiate our handler and start processing events
        handler = MyEventHandler(transcription_stream.output_stream, audio_reader=audio_reader)
        asyncio.gather(audio_reader.read_from_microphone(transcription_stream), handler.handle_events())
        while not handler.finished:
            await asyncio.sleep(1)
        print("Done")

loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()