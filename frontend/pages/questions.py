"""
Questions Page - Display, search, and manage extracted questions.
Enhanced with pagination, inline editing, MCQ quizzes, and AI Q&A.
"""

import streamlit as st
import logging

from database.queries.paper_queries import PaperQueries
from database.queries.question_queries import QuestionQueries
from database.queries.analytics_queries import AnalyticsQueries
from modules.topic_classifier import TopicClassifier
from config.settings import QUESTION_CONFIG
from utils.constants import DIFFICULTY_LEVELS

logger = logging.getLogger(__name__)


def show_questions_page():
    """Display questions bank."""
    try:
        # Get subjects
        subjects = PaperQueries.get_unique_subjects()
        if not subjects:
            st.warning("No questions available yet. Upload exam papers first.")
            return

        # Initialize session state for editing
        if 'editing_q' not in st.session_state:
            st.session_state.editing_q = None

        tab1, tab2, tab3 = st.tabs(["📋 By Subject", "🔍 Search", "🔁 Repeated Questions"])

        # ==========================================
        # TAB 1: By Subject (Paginated)
        # ==========================================
        with tab1:
            st.subheader("Questions by Subject")

            col_sub, col_pad = st.columns([1, 2])
            with col_sub:
                subject = st.selectbox("Select Subject", options=subjects, key="subject_select")

            if subject:
                # Top Filters
                col1, col2, col3 = st.columns(3)
                
                # We need all years/topics for this subject to populate dropdowns
                # For simplicity in large datasets, we'll use PaperQueries to get years
                years = PaperQueries.get_unique_years()
                all_topics = TopicClassifier.get_all_topics()
                topic_names = [t['topic_name'] for t in all_topics]
                
                with col1:
                    filter_type = st.selectbox(
                        "Filter by Type", 
                        options=["All"] + QUESTION_CONFIG.get("types", ["Multiple Choice", "Short Answer", "Long Answer", "Practical"]),
                        key="type_filter"
                    )
                with col2:
                    filter_year = st.selectbox("Filter by Year", options=["All"] + years, key="year_filter")
                with col3:
                    filter_topic = st.selectbox("Filter by Topic", options=["All"] + topic_names, key="topic_filter")

                # Pagination
                if 'page_subject' not in st.session_state:
                    st.session_state.page_subject = 1

                page_size = 20

                questions, total_count = QuestionQueries.get_questions_by_subject_paged(
                    subject, 
                    page=st.session_state.page_subject, 
                    page_size=page_size,
                    filter_type=filter_type if filter_type != "All" else None,
                    filter_year=filter_year if filter_year != "All" else None,
                    filter_topic=filter_topic if filter_topic != "All" else None
                )

                if questions:
                    st.write(f"**Found {total_count} questions** (Showing Page {st.session_state.page_subject})")
                    
                    for q in questions:
                        q_id = q['id']
                        is_editing = (st.session_state.editing_q == q_id)
                        
                        # Build expander label
                        title_prefix = f"Q{q_id}"
                        if q.get('ai_classified'):
                            title_prefix += " 🤖"
                        
                        with st.expander(f"{title_prefix}: {q.get('question_text', '')[:80]}..."):
                            
                            # ---- EDIT MODE ----
                            if is_editing:
                                st.write("✏️ **Edit Question**")
                                with st.form(key=f"edit_form_{q_id}"):
                                    edit_text = st.text_area("Question Text", value=q.get('question_text', ''))
                                    
                                    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                                    with col_e1:
                                        curr_topic = q.get('topic_name')
                                        idx = topic_names.index(curr_topic) if curr_topic in topic_names else 0
                                        edit_topic = st.selectbox("Topic", options=topic_names, index=idx)
                                    with col_e2:
                                        curr_type = q.get('question_type')
                                        types = QUESTION_CONFIG.get("types", [])
                                        t_idx = types.index(curr_type) if curr_type in types else 0
                                        edit_type = st.selectbox("Type", options=types, index=t_idx)
                                    with col_e3:
                                        curr_diff = q.get('difficulty_level', 'Medium')
                                        d_idx = DIFFICULTY_LEVELS.index(curr_diff) if curr_diff in DIFFICULTY_LEVELS else 1
                                        edit_diff = st.selectbox("Difficulty", options=DIFFICULTY_LEVELS, index=d_idx)
                                    with col_e4:
                                        edit_marks = st.number_input("Marks", min_value=0, value=int(q.get('marks_allocated', 0)))
                                        
                                    col_b1, col_b2 = st.columns(2)
                                    with col_b1:
                                        if st.form_submit_button("💾 Save"):
                                            topic_id = TopicClassifier.get_topic_id_by_name(edit_topic)
                                            QuestionQueries.update_question(
                                                question_id=q_id,
                                                topic_id=topic_id,
                                                question_type=edit_type,
                                                difficulty_level=edit_diff,
                                                marks_allocated=edit_marks,
                                                question_text=edit_text
                                            )
                                            st.session_state.editing_q = None
                                            st.rerun()
                                    with col_b2:
                                        if st.form_submit_button("❌ Cancel"):
                                            st.session_state.editing_q = None
                                            st.rerun()
                                            
                            # ---- VIEW MODE ----
                            else:
                                st.write(f"**Full Question:** {q.get('question_text', 'N/A')}")
                                
                                # Metadata badging
                                m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
                                with m_col1:
                                    st.caption(f"**Type:** {q.get('question_type', 'Unknown')}")
                                with m_col2:
                                    topic_str = q.get('topic_name', 'Unclassified')
                                    if q.get('ai_classified'):
                                        topic_str += f" (AI: {int(q.get('topic_confidence', 0)*100)}%)"
                                    st.caption(f"**Topic:** {topic_str}")
                                with m_col3:
                                    st.caption(f"**Year:** {q.get('year', 'N/A')}")
                                with m_col4:
                                    diff = q.get('difficulty_level', 'Medium')
                                    color = "🟢" if diff == "Easy" else "🟠" if diff == "Medium" else "🔴"
                                    st.caption(f"**Difficulty:** {color} {diff}")
                                with m_col5:
                                    st.caption(f"**Marks:** {q.get('marks_allocated', 0)}")
                                
                                # Actions: Edit & Q&A
                                a_col1, a_col2 = st.columns([1, 4])
                                with a_col1:
                                    if st.button("✏️ Edit", key=f"edit_btn_{q_id}"):
                                        st.session_state.editing_q = q_id
                                        st.rerun()
                                
                                # MCQ Options & Quiz Mode
                                if q.get('question_type') == 'Multiple Choice':
                                    options = QuestionQueries.get_question_options(q_id)
                                    if options:
                                        st.markdown("---")
                                        st.write("**Interactive Quiz**")
                                        opt_labels = [f"{o['option_label']}) {o['option_text']}" for o in options]
                                        
                                        user_choice = st.radio("Select an answer:", options=opt_labels, key=f"mcq_{q_id}", index=None)
                                        
                                        if st.button("Check Answer", key=f"check_mcq_{q_id}"):
                                            if user_choice:
                                                selected_label = user_choice.split(')')[0]
                                                with st.spinner("AI is analyzing..."):
                                                    from ai.question_assistant import QuestionAssistant
                                                    opts_for_ai = [{'label': o['option_label'], 'text': o['option_text']} for o in options]
                                                    result = QuestionAssistant.get_mcq_explanation(
                                                        q.get('question_text', ''), 
                                                        opts_for_ai, 
                                                        selected_label,
                                                        subject,
                                                        q.get('topic_name')
                                                    )
                                                    
                                                    if result.get('is_correct'):
                                                        st.success(f"✅ Correct! The answer is {result.get('correct_label')}.")
                                                    else:
                                                        st.error(f"❌ Incorrect. The correct answer is {result.get('correct_label')}.")
                                                    
                                                    st.info(f"**Explanation:** {result.get('explanation')}")
                                            else:
                                                st.warning("Please select an option first.")
                                
                                # General AI Q&A Button
                                else:
                                    if st.button("💡 Get Answer & Explanation", key=f"qa_btn_{q_id}"):
                                        with st.spinner("Generating answer..."):
                                            from ai.question_assistant import QuestionAssistant
                                            ans = QuestionAssistant.get_answer_and_explanation(
                                                q.get('question_text', ''), subject, q.get('topic_name')
                                            )
                                            st.markdown("---")
                                            st.success(f"**Answer:** {ans['answer']}")
                                            st.info(f"**Explanation:** {ans['explanation']}")
                                            if ans['key_points']:
                                                st.write("**Key Points:**\n" + ans['key_points'])
                                            if ans['study_tip']:
                                                st.write(f"🎓 **Study Tip:** {ans['study_tip']}")

                    # Pagination Controls
                    st.markdown("---")
                    p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
                    total_pages = max(1, (total_count + page_size - 1) // page_size)
                    
                    with p_col1:
                        if st.session_state.page_subject > 1:
                            if st.button("⬅️ Previous", key="prev_subj"):
                                st.session_state.page_subject -= 1
                                st.rerun()
                    with p_col2:
                        st.write(f"<div style='text-align: center'>Page {st.session_state.page_subject} of {total_pages}</div>", unsafe_allow_html=True)
                    with p_col3:
                        if st.session_state.page_subject < total_pages:
                            if st.button("Next ➡️", key="next_subj"):
                                st.session_state.page_subject += 1
                                st.rerun()

                else:
                    st.info("No questions found for the selected filters.")

        # ==========================================
        # TAB 2: Smart Search with Live Suggestions
        # ==========================================
        with tab2:
            st.subheader("Search Questions")

            # -- Session state for the search query (allows suggestion clicks to populate it)
            if 'search_query' not in st.session_state:
                st.session_state.search_query = ''
            if 'search_subject_filter' not in st.session_state:
                st.session_state.search_subject_filter = 'All'

            # -- Subject filter
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                search_input = st.text_input(
                    "Search for concepts, topics, techniques...",
                    value=st.session_state.search_query,
                    placeholder="e.g.  binary tree  |  normalization  |  sorting",
                    key="search_input_box",
                    label_visibility="collapsed"
                )
            with search_col2:
                search_subject = st.selectbox(
                    "Subject", options=["All"] + subjects,
                    index=0, key="search_subj_box", label_visibility="collapsed"
                )

            # Sync input to session state
            if search_input != st.session_state.search_query:
                st.session_state.search_query = search_input

            current_query = st.session_state.search_query.strip()

            # ── LIVE SUGGESTIONS (while typing) ──────────────────────────────
            if current_query and len(current_query) >= 2:
                suggestions = QuestionQueries.get_search_suggestions(
                    current_query,
                    subject=search_subject if search_subject != "All" else None,
                    limit=8
                )

                if suggestions:
                    st.markdown("**Suggestions:**")
                    # Show as clickable horizontal pills
                    pill_cols = st.columns(min(len(suggestions), 4))
                    for i, sug in enumerate(suggestions):
                        sug_text = sug['suggestion_text']
                        sug_type = sug.get('suggestion_type', 'topic')
                        q_count = sug.get('question_count', 0)

                        icon = "📌" if sug_type == 'topic' else "📋" if sug_type == 'type' else "📚"
                        label = f"{icon} {sug_text}"
                        if q_count:
                            label += f" ({q_count})"

                        col_idx = i % 4
                        with pill_cols[col_idx]:
                            if st.button(label, key=f"sug_btn_{i}_{sug_text}", use_container_width=True):
                                st.session_state.search_query = sug_text
                                st.rerun()

            # ── POPULAR TOPICS (when idle) ────────────────────────────────────
            elif not current_query:
                st.markdown("**🔥 Popular Topics — click to explore:**")
                popular = QuestionQueries.get_popular_topics(
                    subject=search_subject if search_subject != "All" else None,
                    limit=12
                )
                if popular:
                    # Layout in rows of 4
                    for row_start in range(0, len(popular), 4):
                        row_items = popular[row_start:row_start + 4]
                        p_cols = st.columns(len(row_items))
                        for i, item in enumerate(row_items):
                            with p_cols[i]:
                                label = f"📌 {item['suggestion_text']} ({item['question_count']})"
                                if st.button(label, key=f"pop_{row_start}_{i}", use_container_width=True):
                                    st.session_state.search_query = item['suggestion_text']
                                    st.rerun()
                else:
                    st.info("Upload exam papers to see popular topics here.")

            # ── SEARCH RESULTS ────────────────────────────────────────────────
            if current_query:
                st.markdown("---")
                try:
                    results = QuestionQueries.search_questions(
                        current_query,
                        subject=search_subject if search_subject != "All" else None,
                        limit=50
                    )

                    if results:
                        st.markdown(f"**Found {len(results)} result{'s' if len(results) != 1 else ''} for** `{current_query}`")

                        for i, q in enumerate(results, 1):
                            q_text = q.get('question_text', 'N/A')
                            topic = q.get('topic_name', 'Unclassified')
                            year = q.get('year', 'N/A')
                            subj = q.get('subject', 'N/A')
                            diff = q.get('difficulty_level', 'Medium')
                            marks = q.get('marks_allocated', 0)
                            q_type = q.get('question_type', 'Unknown')
                            ai_flag = q.get('ai_classified', False)
                            relevance = q.get('relevance_score', 0)

                            # Difficulty icon
                            diff_icon = "🟢" if diff == "Easy" else "🟠" if diff == "Medium" else "🔴"
                            # Relevance label
                            rel_label = "🎯 Topic Match" if relevance == 2 else "📝 Text Match"
                            # AI badge
                            ai_badge = " 🤖" if ai_flag else ""

                            expander_title = f"{rel_label} | {topic}{ai_badge} — {q_text[:70]}..."

                            with st.expander(expander_title):
                                st.markdown(f"**Question:** {q_text}")
                                st.markdown("---")

                                r1, r2, r3, r4, r5 = st.columns(5)
                                r1.metric("Subject", subj)
                                r2.metric("Year", str(year))
                                r3.metric("Topic", topic[:18] + "..." if len(topic) > 18 else topic)
                                r4.metric("Difficulty", f"{diff_icon} {diff}")
                                r5.metric("Marks", marks)

                                st.caption(f"Type: {q_type}")

                                # Quick AI Q&A button
                                if st.button("💡 Get Answer", key=f"search_qa_{q.get('id', i)}"):
                                    with st.spinner("Generating answer..."):
                                        from ai.question_assistant import QuestionAssistant
                                        ans = QuestionAssistant.get_answer_and_explanation(
                                            q_text, subj, topic
                                        )
                                        st.success(f"**Answer:** {ans['answer']}")
                                        if ans['explanation']:
                                            st.info(f"**Explanation:** {ans['explanation']}")
                                        if ans['key_points']:
                                            st.write("**Key Points:**\n" + ans['key_points'])
                    else:
                        st.info(f"No results for `{current_query}`. Try a different keyword or a topic name.")
                        # Suggest alternatives
                        fallback = QuestionQueries.get_search_suggestions(
                            current_query[:3], limit=5
                        )
                        if fallback:
                            st.markdown("**Did you mean:**")
                            fb_cols = st.columns(min(len(fallback), 5))
                            for i, fb in enumerate(fallback):
                                with fb_cols[i % 5]:
                                    if st.button(f"📌 {fb['suggestion_text']}", key=f"fb_{i}"):
                                        st.session_state.search_query = fb['suggestion_text']
                                        st.rerun()

                except Exception as e:
                    st.error(f"Search error: {e}")



        # ==========================================
        # TAB 3: Similar & Repeated Questions
        # ==========================================
        with tab3:
            st.subheader("Similar & Repeated Questions")
            st.markdown(
                "Detect questions testing the **same concept, theory, or solving technique** "
                "across different exam papers — even when worded differently."
            )

            # Subject selector for this tab
            sim_subject = st.selectbox(
                "Select Subject to Analyse", options=subjects, key="sim_subject_select"
            )

            # ── LEVEL 1: Topic+Type Grouping (instant, SQL-based) ──────────────
            st.markdown("---")
            st.markdown("### Level 1 — Topic & Technique Similarity")
            st.caption(
                "Groups questions by the **same topic + same question type** across multiple papers. "
                "These groups guarantee the same concept is repeatedly tested."
            )

            try:
                groups = AnalyticsQueries.get_similar_question_groups(sim_subject)

                if groups:
                    st.success(f"**Found {len(groups)} recurring concept groups** across your exam papers.")

                    for grp in groups:
                        topic = grp.get('topic_name', 'Unclassified')
                        q_type = grp.get('question_type', 'Unknown')
                        papers_count = grp.get('papers_count', 0)
                        total_q = grp.get('total_questions', 0)
                        years_str = grp.get('years', 'N/A')
                        avg_marks = grp.get('avg_marks', 0)
                        max_diff = grp.get('max_difficulty', 'Medium')

                        diff_icon = "🟢" if max_diff == "Easy" else "🟠" if max_diff == "Medium" else "🔴"

                        expander_label = (
                            f"📌 {topic} — {q_type} "
                            f"| {papers_count} papers | Years: {years_str}"
                        )

                        with st.expander(expander_label):
                            # Summary row
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("Papers Repeated", papers_count)
                            m2.metric("Total Questions", total_q)
                            m3.metric("Avg Marks", avg_marks)
                            m4.metric("Max Difficulty", f"{diff_icon} {max_diff}")

                            st.markdown("**Questions in this group (by year):**")

                            # Load actual questions from this group
                            try:
                                q_examples = AnalyticsQueries.get_questions_in_group(
                                    sim_subject, topic, q_type, limit=10
                                )
                                for ex in q_examples:
                                    yr = ex.get('year', '?')
                                    d = ex.get('difficulty_level', 'Medium')
                                    d_icon = "🟢" if d == "Easy" else "🟠" if d == "Medium" else "🔴"
                                    mk = ex.get('marks_allocated', 0)
                                    st.markdown(
                                        f"**{yr}** {d_icon} {d} | {mk} marks — "
                                        f"{ex.get('question_text', '')[:200]}..."
                                    )
                                    st.divider()
                            except Exception as ex_err:
                                st.warning(f"Could not load examples: {ex_err}")
                else:
                    st.info(
                        "No recurring concept groups found. "
                        "This could mean questions are very diverse, or only one paper has been uploaded. "
                        "Try uploading more exam papers to see patterns."
                    )

            except Exception as e:
                st.error(f"Error loading similarity groups: {e}")

            # ── LEVEL 2: AI Deep Semantic Scanner ──────────────────────────────
            st.markdown("---")
            st.markdown("### Level 2 — AI Deep Semantic Scan")
            st.caption(
                "Uses Groq AI to find questions that test **identical concepts or techniques** "
                "even if the wording is completely different. "
                "Example: 'Explain BST' and 'Describe a Binary Search Tree' are the same."
            )

            ai_scan_key = f"ai_scan_result_{sim_subject}"

            if st.button("🤖 Run AI Similarity Scan", key="ai_sim_scan_btn", type="primary"):
                with st.spinner("AI is scanning questions for semantic similarities..."):
                    try:
                        from ai.question_assistant import QuestionAssistant
                        questions_batch = AnalyticsQueries.get_all_questions_for_ai_scan(
                            sim_subject, limit=60
                        )

                        if not questions_batch:
                            st.warning("No questions found for this subject.")
                        else:
                            similar_groups = QuestionAssistant.scan_for_ai_similar_groups(
                                questions_batch, subject=sim_subject
                            )
                            st.session_state[ai_scan_key] = similar_groups

                    except Exception as e:
                        st.error(f"AI scan error: {e}")

            # Display AI scan results (persisted in session state)
            if ai_scan_key in st.session_state:
                ai_groups = st.session_state[ai_scan_key]

                if ai_groups:
                    st.success(f"**AI found {len(ai_groups)} semantic similarity groups.**")

                    for grp in ai_groups:
                        label = grp.get('group_label', 'Similar Concept')
                        reason = grp.get('similarity_reason', '')
                        q_list = grp.get('questions', [])

                        with st.expander(f"🧠 {label} ({len(q_list)} similar questions)"):
                            st.info(f"**Why similar:** {reason}")
                            for sq in q_list:
                                yr = sq.get('year', '?')
                                topic = sq.get('topic', 'Unknown')
                                q_text = sq.get('text', '')
                                st.markdown(
                                    f"**{yr}** | Topic: *{topic}* — {q_text[:250]}..."
                                )
                                st.divider()
                else:
                    st.info(
                        "AI found no strong semantic similarities in the current question set. "
                        "This may indicate good question diversity, or you may need more papers uploaded."
                    )

    except Exception as e:
        st.error(f"Error loading questions: {e}")
        logger.error(f"Questions page error: {e}")
