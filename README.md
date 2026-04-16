# QAMini — COVID-19 QA Dashboard

A modern, fully functional one-page QA dashboard web application built with React and FastAPI. The app provides intelligent semantic search-based question answering using CSV datasets with comprehensive statistical analysis.

## Features

✨ **Core Features:**
- 📊 Single-page application (SPA) with no routing
- 🎨 Professional dark/light theme toggle
- 📱 Fully responsive design (desktop, tablet, mobile)
- 🔍 AI-powered semantic similarity search
- 💬 Interactive chat-style QA interface

📈 **Statistical Analysis (8 Experiments):**
1. **Data Visualization** - Histograms, box plots, correlation heatmaps, bar charts
2. **Sampling Techniques** - Random, stratified, systematic, cluster sampling
3. **Correlation & SLR** - Correlation analysis and Simple Linear Regression
4. **Partial & Multiple Correlation** - Advanced correlation metrics
5. **Multiple Linear Regression** - MLR analysis with ANOVA tables
6. **MLE Estimation** - Maximum Likelihood Estimation for distribution fitting
7. **T-Tests** - One-sample and two-sample hypothesis testing
8. **Z-Tests** - Z-test statistical analysis

📥 **Data Upload:**
- Drag & drop CSV file upload
- Automatic dataset validation
- Real-time experiment progress tracking
- Automatic QA pair generation from analysis results

🤖 **AI-Powered Chat:**
- Semantic similarity search using SentenceTransformers
- FAISS vector index for fast retrieval
- Natural language question answering
- Confidence scoring (similarity percentages)

## Tech Stack

### Frontend
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS + PostCSS
- **State Management:** Zustand
- **HTTP Client:** Fetch API

### Backend
- **Framework:** FastAPI with Uvicorn
- **Database:** Local CSV or SQLite (extensible)
- **ML:** SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Search:** FAISS (IndexFlatIP)
- **Statistics:** NumPy, SciPy, Scikit-learn, Pandas
- **Visualization:** Matplotlib

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173/` and the backend API at `http://localhost:8000/`

## Project Structure

```
qamini/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── analyzer.py          # Statistical analysis engine (8 experiments)
│   ├── qa_builder.py        # QA pair generation from analysis results
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── components/      # Reusable UI components
│   │   │   ├── ChatArea.jsx
│   │   │   ├── InputBar.jsx
│   │   │   ├── ExperimentView.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── UploadScreen.jsx
│   │   │   └── MessageBubble.jsx
│   │   ├── index.css        # Global styles
│   │   └── main.jsx         # React entry point
│   ├── package.json
│   └── vite.config.js
└── community.csv            # Sample COVID-19 dataset
```

## API Endpoints

### Upload & Status
- `POST /api/upload` - Upload CSV file
- `GET /api/status` - Get current analysis status
- `GET /api/experiment/{exp_id}` - Get specific experiment results

### Chat & QA
- `POST /api/chat` - Semantic search query

### Health
- `GET /api/health` - Health check endpoint

## Usage

1. **Upload Dataset**
   - Drag & drop a CSV file or click to browse
   - File must have at least 1 numeric column

2. **Wait for Analysis**
   - System automatically runs 8 experiments
   - Progress updates in real-time
   - Results appear as experiments complete

3. **Explore Results**
   - Click experiment tabs to view detailed results
   - View visualizations, statistics, and findings
   - Scroll through data tables

4. **Ask Questions**
   - Switch to "Ask Questions" tab after analysis completes
   - Type questions or click suggested questions
   - Get AI-powered answers based on your data analysis

## Architecture

### Two-Step Processing Pipeline

**Backend Analysis Pipeline:**
1. Data validation & loading
2. Run 8 parallel statistical experiments
3. Generate QA pairs from results
4. Encode questions with SentenceTransformer
5. Build FAISS vector index

**Query Processing:**
1. Encode user question with SentenceTransformer
2. Search FAISS index for top matches
3. Return matched QA pairs with similarity scores

## Performance

- ⚡ **Fast Similarity Search:** FAISS IndexFlatIP with cosine similarity
- 📦 **Efficient Serialization:** Robust JSON encoding for large numpy arrays
- ⏱️ **Real-time Updates:** WebSocket-ready polling mechanism
- 🧵 **Background Processing:** Threaded experiment execution

## Features Demonstrated

✅ Modern React patterns (hooks, composition, state management)
✅ FastAPI best practices (CORS, error handling, async)
✅ Machine learning integration (embeddings, vector search)
✅ Responsive UI design
✅ Data visualization
✅ Real-time processing feedback

## Contributing

This project was built as a full-stack demonstration of:
- AI-powered semantic search
- Statistical analysis automation
- Modern web development practices

## License

MIT License - Feel free to use this as a template for your own projects!

## Support

For issues or questions, please check:
- Backend logs on console
- Browser console for frontend errors
- API responses for debugging

---

**Built with ❤️ using React, FastAPI, and ML**
