# 🧠 Named Entity Recognition (NER) using Transformers (TensorFlow & Keras)

This project demonstrates how to build a **Named Entity Recognition (NER)** model using **Hugging Face Transformers**, trained with **TensorFlow and Keras**, using the popular **CoNLL-2003** dataset.

---

## 📁 Dataset Used
- **Dataset:** `conll2003` (loaded via Hugging Face Datasets)
- **Entities Recognized:** Persons, Organizations, Locations, Miscellaneous

---

## ⚙️ Steps Performed

### ✅ 1. Dataset Loading
- Loaded the **CoNLL-2003** dataset from Hugging Face Datasets library.

### ✅ 2. Tokenization
- Applied tokenization using a pretrained transformer tokenizer (e.g., `bert-base-cased`).
- Special care taken to handle word-to-token alignment.

### ✅ 3. Label Alignment
- Aligned the original word-level labels with tokenized inputs.
- Used special handling to ignore subword tokens in loss computation.

### ✅ 4. Batching & Data Collator
- Implemented batching with Hugging Face’s `DataCollatorForTokenClassification` which also handles label padding correctly for TensorFlow.

### ✅ 5. TensorFlow Dataset Creation
- Converted tokenized dataset into **TensorFlow Dataset** format for both training and validation.

### ✅ 6. Label Mapping
- Mapped integer labels to entity tag names and vice versa for evaluation and decoding.

### ✅ 7. Model Training
- Trained the transformer model using **TensorFlow & Keras**, utilizing the prepared tf datasets.

### ✅ 8. Evaluation
- Evaluated the model using **seqeval** metrics for classification report (Precision, Recall, F1-Score).

### ✅ 9. Inference using Pipeline
- Tested the final model using Hugging Face’s `pipeline("ner")` for easy entity predictions on custom text.

---

## 🔍 Sample Output
```python
Input: "Usama Fiaz lives in Pakistan and works at Google."
Output: [('Usama Fiaz', 'PER'), ('Pakistan', 'LOC'), ('Google', 'ORG')]
