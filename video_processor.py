import yt_dlp
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import os
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, api_key):
        self.groq_client = Groq(api_key=api_key)

    def get_video_id(self, url):
        """Extract video ID from YouTube URL"""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu.be\/([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def process_video(self, video_url):
        """Get transcript from YouTube video"""
        try:
            video_id = self.get_video_id(video_url)
            if not video_id:
                logger.error("Could not extract video ID from URL")
                return None

            logger.info(f"Getting transcript for video ID: {video_id}")
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript pieces into one text
            transcript = ' '.join([entry['text'] for entry in transcript_list])
            
            logger.info(f"Transcript retrieved successfully. Length: {len(transcript)} characters")
            return transcript

        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return None

    def generate_summary(self, transcript):
        """Generate a concise summary using Groq"""
        try:
            if not transcript:
                logger.error("Empty transcript provided")
                return None
            
            logger.info("Generating summary from transcript...")
            
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled content summarizer. Create very concise, clear summaries in 1-2 paragraphs maximum. Focus only on the most important points."
                    },
                    {
                        "role": "user",
                        "content": f"Provide a brief 1-2 paragraph summary of this video transcript, focusing only on the main points:\n\n{transcript}"
                    }
                ],
                temperature=0.3,
                max_tokens=256  # Reduced for shorter summaries
            )
            
            summary = response.choices[0].message.content
            logger.info(f"Summary generated successfully. Length: {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    def answer_question(self, question, transcript):
        """Answer questions about the video"""
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": "Answer questions based on the video transcript provided."
                    },
                    {
                        "role": "user",
                        "content": f"Using this transcript:\n\n{transcript}\n\nQuestion: {question}\n\nAnswer:"
                    }
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return None 