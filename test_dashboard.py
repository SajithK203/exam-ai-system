import sys
sys.path.insert(0, '.')
from database.queries.paper_queries import PaperQueries
from database.queries.analytics_queries import AnalyticsQueries
from modules.analytics_engine import AnalyticsEngine

try:
    subjects = PaperQueries.get_unique_subjects()
    print(f'✓ Subjects: {subjects}')
    
    for subject in subjects:
        analysis = AnalyticsEngine.get_full_analysis(subject)
        print(f'✓ Analysis for {subject}:')
        topics = len(analysis.get('topic_frequency', []))
        types = len(analysis.get('question_type_distribution', []))
        difficulty = len(analysis.get('difficulty_distribution', []))
        years = len(analysis.get('papers_per_year', []))
        print(f'  - Topics: {topics}')
        print(f'  - Types: {types}')
        print(f'  - Difficulty: {difficulty}')
        print(f'  - Years: {years}')
        
        if topics > 0:
            print('✓ Dashboard should display correctly!')
        
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
