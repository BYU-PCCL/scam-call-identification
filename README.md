# Scam Call Identification

(In development) A comprehensive machine learning system for detecting scam phone calls in real time using LLM-derived behavioral features combined with natural language processing techniques. Classifies calls as legitimate or fraudulent, using their transcripts as the raw input.

## Project Overview

This research project, developed by the Perception, Control and Cognition Lab (BYU-PCCL), aims to automatically identify scam phone calls by analyzing conversation patterns, behavioral cues, and linguistic features in call transcripts. The system uses advanced NLP techniques and machine learning models to detect common scam tactics and patterns.

### Key Features

- **Multi-source Data Processing**: Handles transcripts from YouTube scam calls, legitimate call datasets, and real-world call recordings
- **LLM-powered Feature Extraction**: Uses ChatGPT and Gemini models to extract behavioral and linguistic features
- **Behavioral Analysis**: Identifies pressure tactics, urgency patterns, information requests, and authority impersonation
- **Automated Transcription**: Converts audio files to text using state-of-the-art transcription models
- **Docker Support**: Containerized environment for reproducible results
- **Rate Limiting**: Built-in rate limiting for API calls to LLM services

## 📊 Dataset Sources

The project integrates multiple datasets:

- **YouTube Scam Calls**: 243+ transcripts from scam baiting videos and real scam calls
- **Candor Dataset**: Legitimate phone call recordings for comparison
- **Switchboard Dataset**: Standard conversational telephone speech corpus
- **Thai Call Center Dataset**: Additional call center conversation data
- **Internet Search Calls**: Curated collection of scam call examples
- **(and more)**

## Project Structure

```
scam-call-identification/
├── src/                              # Core source code
│   ├── data_processing/              # Data ingestion, preprocessing
│   ├── general_file_utils/           # File handling utils
│   ├── llm_tools/                    # LLM integration and feature extraction
│   ├── ml_scam_classification/       # Main ML classification components
│   │   ├── data/                     # Processed datasets
│   │   ├── models/                   # Model definitions and utils
│   │   ├── prompting/                # LLM prompts and feature definitions
│   │   ├── settings/                 # Configuration files
│   │   └── utils/                    # Utility functions
│   └── rate_limits/                  # API rate limiting
├── scripts/                          # Executable scripts
│   ├── ETL/                          # Extract, Transform, Load operations
│   ├── EDA/                          # Exploratory Data Analysis
│   ├── feature_engineering/          # Feature extraction scripts
│   └── generating-synthetic-calls/   # Synthetic data generation
├── outputs/                          # Generated results and models
├── Dockerfile                        # Container configuration
├── requirements.txt                  # Python dependencies
└── build_image_docker_scams.sh       # Docker build script
```

## Using the Repo

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- API keys for OpenAI GPT and Google Gemini (for feature extraction)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BYU-PCCL/scam-call-identification.git
   cd scam-call-identification
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv scams_env
   # On Windows:
   .\scams_env\Scripts\activate
   # On Linux/Mac:
   source scams_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Docker Setup (Alternative)

Build and run using Docker:
```bash
chmod +x build_image_docker_scams.sh
./build_image_docker_scams.sh
```

### API Configuration

1. Create an `api_keys` folder in the project root
2. Add your API keys for:
   - OpenAI GPT models
   - Google Gemini models
3. Configure rate limits in `src/rate_limits/` directory

## Usage

### Running Scripts

**Important**: Always run scripts as modules to ensure proper imports:

```bash
python -m scripts.feature_engineering.run_chatgpt_behavioral_analysis
python -m scripts.ETL.aggregate_all_transcripts
python -m scripts.EDA.compiled.inspect_compiled_transcripts
```

### Feature Extraction

Extract behavioral features from call transcripts:

```bash
python -m scripts.feature_engineering.run_chatgpt_behavioral_analysis [prompt_path] [continuation_prompt_path]
```

### Data Processing

Process raw audio files and generate transcripts:

```bash
python -m scripts.ETL.transcribe_audio
python -m scripts.ETL.transform_parquet_to_audio
```

### Behavioral Analysis

The system analyzes calls across multiple behavioral dimensions:

1. **Pressure & Urgency**: Detecting time pressure and fear tactics
2. **Information Elicitation**: Identifying requests for sensitive data
3. **Authority Impersonation**: Recognizing false authority claims
4. **Financial Request Patterns**: Detecting payment solicitations
5. **Conversation Flow**: Analyzing dialogue patterns
6. **Scam-Specific Signatures**: Identifying known scam types

## 📈 Model Performance

The system uses a hierarchical classification approach:

- **Feature Extraction**: LLM-based behavioral feature extraction
- **Classification**: Traditional ML models trained on extracted features
- **Validation**: Cross-validation on multiple datasets

## 🔬 Research Features

### Behavioral Feature Categories

The system analyzes calls across 9+ behavioral categories:

1. **Pressure & Urgency Tactics**
2. **Information Elicitation Patterns**
3. **False Authority & Impersonation**
4. **True Authority & Legitimacy**
5. **Financial Request Patterns**
6. **Conversation Flow & Meta-Communication**
7. **Question Patterns & Information Seeking**
8. **Response Patterns & Compliance**
9. **Scam Signature Behaviors**

### Advanced Features

- **Multi-LLM Analysis**: Compares results from different language models
- **Temporal Analysis**: Tracks behavioral patterns over conversation duration
- **Synthetic Data Generation**: Creates training data using demographic models
- **Rate-Limited Processing**: Manages API calls efficiently

## 📝 Configuration

### Prompt Engineering

Prompts are versioned and stored in `src/ml_scam_classification/prompting/`:
- `features.json` / `features_v2.json`: Behavioral feature definitions
- `prompt_conner_v*.txt`: Main analysis prompts
- `prompt_*_contd.txt`: Continuation prompts for long conversations

### Settings

Configuration files in `src/ml_scam_classification/settings/`:
- `global_settings.py`: Global configuration
- `supported_transcription_models.json`: Available transcription models
- Rate limiting configurations

## 🧪 Testing and Validation

The project includes comprehensive testing utilities:

- **File validation**: Ensures data integrity
- **JSON validation**: Validates structured outputs
- **Path validation**: Confirms file system operations
- **Model validation**: Tests classification performance

## 📊 Output Formats

The system generates:
- **JSON Feature Files**: Structured behavioral analysis results
- **CSV Reports**: Aggregated classification results
- **Transcription Files**: Processed audio-to-text conversions
- **Model Artifacts**: Trained classification models

## 🤝 Contributing

This is a research project. For contributions:

1. Follow the existing code structure
2. Use the module-based import system
3. Add appropriate error handling and validation
4. Include comprehensive documentation
5. Test with multiple datasets

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏛️ Institution

**Brigham Young University - Perception, Control and Cognition Lab (BYU-PCCL)**

## 📚 Citation

If you use this work in your research, please cite:

```bibtex
@software{scam_call_identification,
  title={Scam Call Identification System},
  author={BYU Perception, Control and Cognition Lab},
  year={2025},
  url={https://github.com/BYU-PCCL/scam-call-identification}
}
```

## Research Applications

Once fully developed, this system could be applied to:
- **Telecommunications Security**: Real-time scam call detection
- **Consumer Protection**: Educational tools for scam awareness
- **Law Enforcement**: Analysis of fraud patterns
- **Academic Research**: Study of deceptive communication patterns
- **Industry Applications**: Call center quality assurance

---

For questions, issues, or research collaboration opportunities, please open an issue or contact the BYU-PCCL team.