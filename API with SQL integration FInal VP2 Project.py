import sqlite3
import tkinter
import openai
import random
import re



class BlackBox:
    def __init__(self):
        self.initialize_database()
        self.initialize_openai()
        self.follow_up_questions = []  # List to store follow-up questions
        self.level1_id = None  # Initialize level1_id to None

        # Initialize Main Window
        self.main_window = tkinter.Tk()
        self.main_window.title('BLACK BOX OF INFORMATION')
        self.main_window.geometry('800x800')

        # Create top frames
        self.top_frame = tkinter.Frame(self.main_window)
        self.top_frame.pack()

        # Create middle frame
        self.middle_frame = tkinter.Frame(self.main_window)
        self.middle_frame.pack()

        # Button frames
        self.button_frame = tkinter.Frame(self.main_window)
        self.button_frame.pack()

        # Create bottom frame
        self.bottom_frame = tkinter.Frame(self.main_window)
        self.bottom_frame.pack()

        # Create and pack labels
        self.intro1_label = tkinter.Label(self.top_frame, text="Enter Your Question: ", font=("Helvetica", 22, "bold"),
                                          width=18, height=3)
        self.intro1_label.pack(side="left")

        # StringVar for prompt and the API response
        self.prompt_var = tkinter.StringVar()
        self.output_var = tkinter.StringVar()

        # Create and pack entry widget for user prompt
        prompt_entry = tkinter.Entry(self.top_frame, textvariable=self.prompt_var, font=("Helvetica", 22), width=38)
        prompt_entry.pack(side="right")

         # Create and pack a Text widget for displaying the API message
        self.api_response_text = tkinter.Text(self.middle_frame, wrap=tkinter.WORD, height=10, width=100, font=("Helvetica", 22))
        self.api_response_text.pack(fill=tkinter.BOTH, expand=True)

        # Create a vertical scrollbar and associate it with the Text widget
        #scrollbar_api_response = tkinter.Scrollbar(self.middle_frame, command=self.api_response_text.yview)
        #scrollbar_api_response.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        #self.api_response_text.config(yscrollcommand=scrollbar_api_response.set)

        # Create a button to retrieve the user's prompt
        get_answer_button = tkinter.Button(self.button_frame, text="Get Answer", command=self.get_prompt, height=2,
                                          width=15, font=("Helvetica", 18, "bold"))
        get_answer_button.pack(side='left')

        # Create button to view conversation log
        view_log_button = tkinter.Button(self.button_frame, text="View Conversation Log", command=self.view_log,
                                         height=2, width=20, font=("Helvetica", 18, "bold"))
        view_log_button.pack(side='right')

         # Create button for data export, collation, and report display
        collate_button = tkinter.Button(self.button_frame, text='Export and Collate Data', command=self.export_and_collate_data,
                                        height=2, width=25, font=("Helvetica", 18, "bold"))
        collate_button.pack()

        # Create button Exit GUI
        exit_button = tkinter.Button(self.bottom_frame, text='EXIT', command=self.exit_and_clear_log, height=2,
                                     width=15, font=("Helvetica", 18, "bold"))
        exit_button.pack()

        # Create and pack a Listbox for displaying the follow-up questions
        #self.follow_up_listbox = tkinter.Listbox(self.middle_frame, selectmode=tkinter.SINGLE, height=1, width=50, font=("Helvetica", 22))
        #self.follow_up_listbox.pack(fill=tkinter.BOTH, expand=True)

        # Create a vertical scrollbar and associate it with the Listbox
        #scrollbar_follow_up = tkinter.Scrollbar(self.middle_frame, command=self.follow_up_listbox.yview)
        #scrollbar_follow_up.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        #self.follow_up_listbox.config(yscrollcommand=scrollbar_follow_up.set)

        # Create and pack a label for follow-up questions
        follow_up_label = tkinter.Label(self.middle_frame, text="Select a Follow-up Question:", font=("Helvetica", 22, "bold"))
        follow_up_label.pack()

        # Create and pack a Listbox for displaying the follow-up questions
        self.follow_up_listbox = tkinter.Listbox(self.middle_frame, selectmode=tkinter.SINGLE, height=10, width=50, font=("Helvetica", 18))
        self.follow_up_listbox.pack(fill=tkinter.BOTH, expand=True)
        # Configure a horizontal scrollbar for the Listbox
        scrollbar_follow_up_horizontal = tkinter.Scrollbar(self.middle_frame, orient=tkinter.HORIZONTAL)
        scrollbar_follow_up_horizontal.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.follow_up_listbox.config(xscrollcommand=scrollbar_follow_up_horizontal.set)
        scrollbar_follow_up_horizontal.config(command=self.follow_up_listbox.xview)


        # Create a button to get the selected follow-up response
        get_follow_up_button = tkinter.Button(self.button_frame, text='Get Follow-up Response',
                                              command=self.get_follow_up_response, height=2,
                                              width=25, font=("Helvetica", 18, "bold"))
        get_follow_up_button.pack()

        # Infinite Loop to keep the program running until the user exits
        tkinter.mainloop()

    def initialize_database(self):
        # Create connection to SQLite server
        conn = sqlite3.connect('conversation.db')
        cursor = conn.cursor()

        # Create tables if they do not exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS level1
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           prompt TEXT,
                           response TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS level2
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          level1_id INTEGER,
                          question TEXT,
                          response TEXT)''')

        # commit and close connection to the database
        conn.commit()
        conn.close()

    def get_prompt(self):
        prompt = self.prompt_var.get()

        if not prompt:
            error_message = "Error: Please enter a question."
            self.display_response(error_message, is_error=True)
            return

        try:
            api_response = self.generate_response(prompt)
            self.display_response(api_response)

            # Process API response to generate follow-up questions
            self.process_api_response(api_response)

            # Insert the conversation into the database
            self.insert_level1_conversation(prompt, api_response)

            # Generate follow-up questions
            self.generate_follow_up_questions()
        except Exception as e:
            error_message = f"Error: An unexpected error occurred - {str(e)}"
            self.display_response(error_message, is_error=True)

    def process_api_response(self, api_response):
        # Clear existing follow-up questions
        self.follow_up_questions = []

        # Split the API response into a list of follow-up questions
        follow_up_questions = api_response.split('\n')  # Modify this based on the actual response structure

        # Store follow-up questions
        self.follow_up_questions.extend(follow_up_questions)

        # Display follow-up questions in a Listbox for the user to choose
        self.display_follow_up_questions()

    def insert_level1_conversation(self, prompt, response):
        # Create connection to SQLite server
        conn = sqlite3.connect('conversation.db')
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO level1 (prompt, response)
                          VALUES (?, ?)''', (prompt, response))

        # Get the last inserted row id (level1_id) and set it as the instance variable
        self.level1_id = cursor.lastrowid

        # commit and close connection to the database
        conn.commit()
        conn.close()

    def insert_level2_conversation(self, level1_id, question, response):
        conn = sqlite3.connect("conversation.db")
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO level2 (level1_id, question, response) VALUES (?, ?, ?)''',
                       (level1_id, question, response))
        conn.commit()
        conn.close()

    def initialize_openai(self):
        api_key = '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'
        openai.api_key = api_key

    def generate_response(self, prompt):
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=100,
            temperature=0.8  # Adjust the temperature for better sentence completion
        )
        return response.choices[0].text.strip()

    

    def display_response(self, response, is_error=False):
        # Clear the existing content in the Text widget
        self.api_response_text.delete("1.0", tkinter.END)

        # Insert the generated response into the Text widget
        self.api_response_text.insert(tkinter.END, response)

        # Update the StringVar for displaying the API response
        if is_error:
            response = f"ERROR: {response}"

        self.output_var.set(response)

        

    def generate_follow_up_questions(self):
        # Get the API response
        api_response = self.api_response_text.get("1.0", tkinter.END)

        if not api_response:
            # Handle the case where there's no API response
            return

        # Extract keywords from the API response
        keywords = self.extract_keywords(api_response)

        # Generate follow-up questions based on keywords
        self.follow_up_questions = self.generate_follow_ups_from_keywords(keywords, num_variations=3)

        # Clear the existing content in the Listbox
        self.follow_up_listbox.delete(0, tkinter.END)

        # Insert the generated questions into the Listbox
        for question in self.follow_up_questions:
            self.follow_up_listbox.insert(tkinter.END, question)
            

    def extract_keywords(self, text):
        # Use regular expression to find words containing only alphabets (excluding numbers and symbols)
        words = re.findall(r'\b[A-Za-z]+\b', text)
        # Consider words with more than three characters as keywords (you can adjust this threshold)
        keywords = [word.lower() for word in words if len(word) > 3]
        return keywords
    

    def generate_follow_ups_from_keywords(self, keywords, num_variations):
        # Generate follow-up questions by incorporating each keyword
        follow_ups = set()  # Use a set to avoid duplicates
        for keyword in keywords:
            for _ in range(num_variations):
                # You can customize the template for generating follow-up questions
                variation = f"How does {keyword} relate to {self.prompt_var.get()}?"
                follow_ups.add(variation)

        return list(follow_ups)  # Convert set back to a list for insertion into Listbox  


    def generate_variations(self, text, num_variations):
        # Split the text into words
        words = text.split()

        # Generate variations by shuffling the words
        variations = []
        for _ in range(num_variations):
            random.shuffle(words)
            variation = ' '.join(words)
            variations.append(variation)

        return variations
    

    def get_follow_up_response(self):
        # Get the selected follow-up question from the follow-up listbox
        selected_index = self.follow_up_listbox.curselection()

        if selected_index:
            selected_text = self.follow_up_listbox.get(selected_index[0])

            # Send the selected question to the API for a response
            follow_up_response = self.generate_response(selected_text)

            # Display the follow-up response
            self.display_response(follow_up_response)

            # Insert the follow-up conversation into the database
            self.insert_level2_conversation(self.level1_id, selected_text, follow_up_response)

    def display_follow_up_questions(self):
        # Clear the existing items in the Listbox
        self.follow_up_listbox.delete(0, tkinter.END)

        # Insert the generated questions into the Listbox
        for question in self.follow_up_questions:
            self.follow_up_listbox.insert(tkinter.END, question)

    def view_log(self):
        # Retrieve data from both level1 and level2 tables in the database
        conn = sqlite3.connect('conversation.db')
        cursor = conn.cursor()

        # Fetch data from level1 table
        cursor.execute('SELECT prompt, response FROM level1')
        level1_data = cursor.fetchall()

        # Fetch data from level2 table
        cursor.execute('SELECT question, response FROM level2')
        level2_data = cursor.fetchall()

        conn.close()

        # Display the conversation log in a new window
        log_window = tkinter.Toplevel(self.main_window)
        log_window.title('Conversation Log')

        # Create a text widget to display the conversation log
        log_text = tkinter.Text(log_window, wrap=tkinter.WORD)
        log_text.pack()

        # Insert data from level1 into the text widget
        log_text.insert(tkinter.END, "=== Level 1 ===\n\n")
        for entry in level1_data:
            log_text.insert(tkinter.END, f"Prompt: {entry[0]}\nResponse: {entry[1]}\n\n")

        # Insert data from level2 into the text widget
        log_text.insert(tkinter.END, "=== Level 2 ===\n\n")
        for entry in level2_data:
            log_text.insert(tkinter.END, f"Question: {entry[0]}\nResponse: {entry[1]}\n\n")

    def retrieve_log_data(self):
        conn = sqlite3.connect('conversation.db')
        cursor = conn.cursor()

        # Assuming you only want data from the level1 table for simplicity
        cursor.execute('SELECT prompt, response FROM level1')
        log_data = cursor.fetchall()

        conn.close()
        return log_data


    def export_and_collate_data(self):
        # Retrieve data from the database
        data_from_database = self.retrieve_log_data()

        # Extract prompts and responses from the data
        prompts_and_responses = [(entry[0], entry[1]) for entry in data_from_database]

        # Split data into chunks if needed
        data_chunks = [prompts_and_responses[i:i + 5] for i in range(0, len(prompts_and_responses), 5)]

        # Initialize an empty list to store summarized reports
        summarized_reports = []

        # Iterate through each chunk of data
        for chunk in data_chunks:
            # Generate summaries for each prompt-response pair in the chunk
            summaries = [self.summarize_response(response) for _, response in chunk]
            
            # Combine prompts, responses, and summaries into a single report
            report = "\n".join(f"Prompt: {prompt}\nResponse: {response}\nSummary: {summary}\n" for (prompt, response), summary in zip(chunk, summaries))
            
            # Append the report to the list
            summarized_reports.append(report)

        # Concatenate summarized reports
        collated_report = "\n".join(summarized_reports)

        # Print some debugging information
        print("Data from database:", data_from_database)
        print("Summarized report:", collated_report)

        # Display the collated report in a new window
        self.display_collated_report(collated_report)

    def summarize_response(self, response, max_tokens=100):
        # Split the response into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', response)

        # Initialize variables
        summary_tokens = 0
        summary_sentences = []

        # Iterate through sentences until the token limit is reached
        for sentence in sentences:
            sentence_tokens = len(sentence.split())
            if summary_tokens + sentence_tokens <= max_tokens:
                summary_sentences.append(sentence)
                summary_tokens += sentence_tokens
            else:
                break

        # Join the selected sentences to form the summary
        summarized_response = ' '.join(summary_sentences)

        return summarized_response



    def collate_and_summarize_data(self, data):
        # Concatenate prompts and responses into a single string
        collated_data = "\n".join(data)
        return collated_data


    
    def display_collated_report(self, report):
        # Create a new window to display the collated report
        report_window = tkinter.Toplevel(self.main_window)
        report_window.title('Collated Report')

        # Create a text widget to display the collated report
        collated_report_text = tkinter.Text(report_window, wrap=tkinter.WORD)
        collated_report_text.pack()

        # Configure tags for bold text
        collated_report_text.tag_configure('bold', font=('Helvetica', 12, 'bold'))

        # Insert the collated report into the text widget
        lines = report.split('\n')
        for line in lines:
            if line.startswith("Prompt:") or line.startswith("Response:") or line.startswith("Summary:"):
                label, content = line.split(":", 1)
                collated_report_text.insert(tkinter.END, f"{label}:", 'bold')
                collated_report_text.insert(tkinter.END, f"{content}\n")
            else:
                collated_report_text.insert(tkinter.END, line + '\n')


        

    def exit_and_clear_log(self):
        conn = sqlite3.connect('conversation.db')
        cursor = conn.cursor()

        # Clear data from both level1 and level2 tables
        cursor.execute('DELETE FROM level1')
        cursor.execute('DELETE FROM level2')

        conn.commit()
        conn.close()

        # Destroy the main window
        self.main_window.destroy()
        


if __name__ == "__main__":
    blackbox = BlackBox()





