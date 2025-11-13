# FAQ

**Q: Why doesn't ElevenLabs work anymore?**
A: The project has migrated to Kokoro for cost-effectiveness. ElevenLabs code is retained for backward compatibility but is not actively used.

**Q: Can I use custom voices?**
A: Yes, Kokoro supports multiple voice options. See the Advanced Configuration section for details.

**Q: Is GPU acceleration supported?**
A: Yes, if PyTorch is configured with CUDA support, the Kokoro model will automatically use GPU acceleration.

**Q: How do I handle long texts?**
A: The system automatically splits long texts at newlines. For very long texts, consider splitting them manually into smaller chunks.

**Q: Can I use this in production?**
A: Yes, but ensure you test thoroughly with your specific hardware and use case. The module includes robust error handling for production use.
