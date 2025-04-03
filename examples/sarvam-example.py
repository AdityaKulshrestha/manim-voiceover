from manim import *
from manim_voiceover import VoiceoverScene 
from manim_voiceover.services.sarvam import SarvamTTS

class SarvamExample(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            SarvamTTS()
        )
        circle = Circle()
        square = Square().shift(2*RIGHT)

        with self.voiceover(text="This is circle is drawn as I speak") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

        with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
            self.play(circle.animate.shift(2 * LEFT), run_time=tracker.duration)

        self.wait()