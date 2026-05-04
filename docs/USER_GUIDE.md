# User Guide

## Getting Started

### First Login
1. Navigate to http://localhost:8501
2. You'll see the home page with system overview
3. Check "System Status" in sidebar - ensure DB is connected

## Main Features

### 📤 Upload Paper

**Steps:**
1. Click "📤 Upload Paper" in navigation
2. Select PDF exam paper
3. Enter subject name (e.g., "Computer Science")
4. Enter exam year
5. Click "🚀 Process PDF"

**Processing:**
- System extracts questions (Step 1/4)
- Cleans text (Step 2/4)
- Parses questions (Step 3/4)
- Classifies topics (Step 4/4)

**Output:**
- Summary showing questions found
- Sample questions preview
- Success/error messages

### 📊 Analysis Dashboard

**Features:**
1. **Subject Selection**: Choose subject to analyze
2. **Topic Frequency**: Bar chart showing most asked topics
3. **Question Types**: Pie chart of MCQ vs Long Answer
4. **Difficulty Distribution**: Easy/Medium/Hard breakdown
5. **Year Trends**: Timeline of papers
6. **Statistics**: Summary metrics

**How to Use:**
- Select subject from dropdown
- View visualizations automatically
- Hover over charts for details
- Check "Statistics Summary" for key numbers

### ❓ Question Bank

**Three Views:**
1. **By Subject**
   - Select subject
   - Filter by type, year, topic
   - Click to expand and see full question

2. **Search**
   - Enter keywords (e.g., "binary tree", "algorithm")
   - System searches question text
   - Results show year and subject

3. **Repeated Questions**
   - Shows questions appearing in multiple papers
   - Indicates how many times repeated
   - Useful for understanding important topics

### 🤖 AI Insights

**Insight Types:**

1. **📚 Study Plan**
   - AI-generated study recommendations
   - Top topics to focus on
   - Prioritized learning strategy

2. **📝 Mock Exam Suggestions**
   - How to create effective mock exams
   - Recommended topic distribution
   - Suggested difficulty mix

3. **⚠️ Weak Areas**
   - Topics students typically struggle with
   - Why these are important
   - How to overcome challenges

4. **⏱️ Time Management**
   - Time allocation per topic
   - Section strategy for exams
   - Pacing guidelines

**How to Use:**
1. Select subject
2. Choose insight type
3. Click "🚀 Generate Insights"
4. Read AI-generated recommendations

### 📝 Mock Exam

**Configuration:**
1. **Subject**: Choose subject
2. **Questions**: Set count (5-50)
3. **Question Distribution**: Set % MCQ, Short Answer, Long Answer
4. **Difficulty**: Set % Easy, Medium, Hard

**Steps:**
1. Configure settings
2. Click "🎯 Generate Mock Exam"
3. System selects questions based on settings
4. Review and answer questions
5. Click "📥 Save Answers" when done

**Features:**
- Questions displayed with metadata
- Text area for writing answers
- Progress tracking
- Can generate new exam anytime

## Tips & Tricks

### Maximize Learning

1. **Upload Multiple Years**: Get better patterns with more data
2. **Review Repeated Questions**: These appear frequently
3. **Focus on Top Topics**: Spend 70% time on top 5 topics
4. **Use Mock Exams**: Take them regularly for practice
5. **Check Trends**: Notice which topics increase/decrease

### For Teachers

1. **Analyze Student Patterns**: Upload student answer sheets
2. **Identify Common Mistakes**: See which topics cause issues
3. **Plan Curriculum**: Adjust teaching based on frequency
4. **Create Better Exams**: Use recommended distribution

### For Students

1. **Start with Analysis**: See what's important
2. **Read Top Questions**: Understand patterns
3. **Get Recommendations**: Follow AI guidance
4. **Practice with Mocks**: Build exam confidence
5. **Track Progress**: Improve mock exam scores

## Common Issues

### PDF Won't Upload
- **Check**: File is valid PDF
- **Check**: File size < 50MB
- **Check**: File not corrupted
- **Solution**: Try different PDF

### No Questions Extracted
- **Possible**: PDF has only images
- **Possible**: Text is scanned/blurry
- **Solution**: Use text-based PDF

### Topics Not Recognized
- **Note**: System uses keyword matching
- **Solution**: Can manually set topics
- **Note**: More data improves classification

### Slow Analysis
- **Note**: First analysis takes longer
- **Note**: Results are cached after
- **Solution**: Allow 30 seconds for analysis

### API Errors
- **Check**: Groq API key in .env
- **Check**: Internet connection
- **Solution**: Restart application

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+K | Search questions |
| Ctrl+G | Generate mock exam |
| Ctrl+A | Analyze dashboard |
| Ctrl+I | Get insights |

## Best Practices

### Data Management
✅ Upload papers chronologically (oldest first)  
✅ Use consistent subject names  
✅ Regularly backup database  
✅ Archive old analysis results  

### Question Organization
✅ Ensure questions are properly formatted  
✅ Include marks if available  
✅ Use full questions (not summaries)  
✅ Maintain consistent year format  

### Analysis
✅ Analyze after uploading multiple papers  
✅ Compare years to see trends  
✅ Generate multiple mock exams  
✅ Review weak areas systematically  

## Accessibility

The system is designed for:
- 📱 Desktop browsers (recommended)
- 💻 Tablets
- ⌚ Large screens

**Supports:**
- Dark/Light mode
- Keyboard navigation
- Text scaling

## Privacy & Security

- All data stored locally in MySQL
- No data sent to external services (except Groq API)
- Passwords encrypted
- Session timeouts after 30 minutes
- File uploads scanned for integrity

## Getting Help

1. **Read Documentation**: Check `/docs` folder
2. **Check Logs**: See `/logs` for error details
3. **Contact Support**: Email support@examanalysis.com
4. **Report Bug**: Create GitHub issue

## FAQ

**Q: Can I delete papers?**
A: Yes, from Analysis page - select paper and delete

**Q: Export questions?**
A: Yes, from Question Bank - download as CSV

**Q: Multiple users?**
A: Currently single-user - future versions will support teams

**Q: Backup data?**
A: Use MySQL backup: `mysqldump -u root -p database > backup.sql`

**Q: How accurate is AI?**
A: Depends on data quality and quantity. Improve with more papers.

---

For detailed technical information, see [Architecture](ARCHITECTURE.md) and [API Reference](API_REFERENCE.md).
