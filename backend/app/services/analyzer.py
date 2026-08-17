class AnalyzerService:

    def analyze_sentiment(self, text: str):

        text = text.lower()

        score = 0

        positive_words = ["happy", "good", "great", "love"]
        negative_words = ["sad", "bad", "angry", "hate"]

        for word in positive_words:
            if word in text:
                score += 1

        for word in negative_words:
            if word in text:
                score -= 1

        if score > 0:
            return "Positive sentiment 😊"
        elif score < 0:
            return "Negative sentiment 😢"
        else:
            return "Neutral sentiment 😐"