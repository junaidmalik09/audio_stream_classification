import torch
import torch.nn as nn
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification


def id2label(id, classes=["male", "female", "ambient"]):
    """
    Convert an integer ID to a corresponding label.

    Args:
        id (int): The ID to convert.
        classes (list of str): A list of class labels.

    Returns:
        str: The label corresponding to the given ID.
    """
    return classes[id]


class BatchedInferenceWithThreshold(nn.Module):
    """
    A neural network module for batched inference with a threshold on RMS value.

    Attributes:
        feature_extractor (AutoFeatureExtractor): feature extractor for audio data.
        classifier (AutoModelForAudioClassification): classifier model for audio classification.
        threshold (float): RMS threshold for determining if inference should be run.
    """

    def __init__(self, model_name, threshold=0.1):
        """
        Initialize the BatchedInferenceWithThreshold module.

        Args:
            model_name (str): The name of the pretrained model to use.
            threshold (float): The RMS threshold for inference. Default is 0.1.
        """
        super(BatchedInferenceWithThreshold, self).__init__()
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.classifier = AutoModelForAudioClassification.from_pretrained(model_name)
        self.threshold = threshold

    def forward(self, audio_data_batch):
        """
        Perform forward pass for batched audio data with RMS thresholding.

        Args:
            audio_data_batch (torch.Tensor)
             tensor of shape (batch_size, num_samples) representing audio data batch.

        Returns:
            int or torch.Tensor: Returns -1 if the RMS value is below the threshold, otherwise returns the mode of predicted labels.
        """
        rms_value = torch.sqrt(torch.mean(audio_data_batch**2, dim=1)).mean().item()
        if rms_value < self.threshold:
            return -1
        else:
            features = self.feature_extractor(
                audio_data_batch,
                return_tensors="pt",
                sampling_rate=16000,
                padding="longest",
            )
            predicted_logits = self.classifier(features["input_values"].squeeze(0)).logits
            predicted_labels = predicted_logits.argmax(dim=-1)
            return torch.mode(predicted_labels, dim=0).values.item()
