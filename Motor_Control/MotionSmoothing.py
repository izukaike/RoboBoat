class MotionSmoothing:
    def __init__(self, numSamples, defaultValue = 0):
        self.numSamples = numSamples
        self.history = [defaultValue] * numSamples
        self.sum = numSamples * defaultValue

    def addSample(self, newVal):
        self.sum -= self.history.pop(0)
        self.sum += newVal
        self.history.append(newVal)
        return self.sum / self.numSamples

    def evaluate(self):
        return self.sum / self.numSamples
        