# Required libraries
import streamlit as st
import pandas as pd
import io
from streamlit_modal import Modal

# Function to process Excel file and store in session state
def load_and_store_excel(file):
    df = pd.read_excel(file)
    st.session_state.data = df
    st.session_state.unassigned_questions = df[df['courses'].isna()]

# Function to create a modal popup for question details
def question_details_modal(question_row, title):
    modal = Modal(key=title, title=title)
    open_modal = st.button(label=title)
    if open_modal:
        with modal.container():
            st.markdown("**Question:** " + question_row['questions'])
            st.markdown("**Course Assigned:** " + str(question_row['courses']))
            for answer_label in ['A', 'B', 'C', 'D', 'E']:
                st.markdown(f"**{answer_label}:** {question_row.get(answer_label, '')}")
# Function to assign course and update the interface
def assign_course(data, question, course, current_index):
    data.loc[data['questions'] == question, 'courses'] = course
    st.session_state.data = data
    st.success(f"Course '{course}' assigned to question '{question}'")
    if current_index + 1 < len(st.session_state.unassigned_questions):
        st.session_state.current_index += 1
        st.experimental_rerun()

# Main Streamlit App Function
def main():
    st.title("Course Assignment Interface")

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=['xlsx'])

    if uploaded_file is not None:
        # Load and store the data in session state if not already done
        if 'data' not in st.session_state:
            load_and_store_excel(uploaded_file)

        data = st.session_state.data
        questions = st.session_state.unassigned_questions

        if len(questions) > 0:
            # Managing the current question index
            if 'current_index' not in st.session_state:
                st.session_state.current_index = 0
            
            current_index = st.session_state.current_index
            question_row = questions.iloc[current_index]
            question = question_row['questions']

            # Display questions
            st.write("Question:", question)
            # Display Probable Courses in Horizontal Layout
            cols = st.columns(6)  # Creating six columns
            for i in range(1, 7):
                probable_course = question_row.get(f'probablecourse{i}', '')
                if probable_course and cols[i - 1].button(probable_course, key=f'probable_course_{i}'):
                    assign_course(data, question, probable_course, current_index)

            # Manual Course Entry
            course = st.text_input("Or Enter Course Manually")
            if st.button("Assign Manual Course"):
                assign_course(data, question, course, current_index)

            # Modal popup for the previous question details
            if current_index > 0:
                prev_question_row = questions.iloc[current_index - 1]
                question_details_modal(prev_question_row, "Previous Question Details")

            # Modal popup for the current question answers
            question_details_modal(question_row, "Current Question Answers")

            # Export Excel File
            if st.button("Export Final Excel File"):
                # Convert DataFrame to Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    st.session_state.data.to_excel(writer, index=False)
                st.download_button(label="Download Excel File", 
                                   data=output, 
                                   file_name="final_data.xlsx", 
                                   mime="application/vnd.ms-excel")
        else:
            st.write("All questions have been assigned courses.")

# Run the app
if __name__ == "__main__":
    main()
