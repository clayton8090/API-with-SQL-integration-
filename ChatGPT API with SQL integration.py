import sqlite3
import tkinter
import openai




class BlackBox:
  def __init__(self):
      self.initialize_database()
      self.initialize_openai()
      self.initialize_gui()


  def initialize_gui(self):
  
      # Initialize Main Window
      self.main_window = tkinter.Tk()
      self.main_window.title('BLACK BOX OF INFORMATION')
      self.main_window.geometry('800x600')


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
      self.intro1_label = tkinter.Label(self.top_frame, text="Enter Your Question: ", font=("Helvetica", 14, "bold"), width=18, height=3)
      self.intro1_label.pack(side="left")


      # StringVar for prompt and the API response
      self.prompt_var = tkinter.StringVar()
      self.output_var = tkinter.StringVar()


      # Create and pack entry widget for user prompt
      prompt_entry = tkinter.Entry(self.top_frame, textvariable=self.prompt_var, font=("Helvetica", 14), width=38)
      prompt_entry.pack(side="right")


      # Create and pack a text widget for displaying the API message
      self.api_response_text = tkinter.Text(self.middle_frame, wrap=tkinter.WORD, height=18, font=("Helvetica", 12))
      self.api_response_text.pack(fill=tkinter.BOTH, expand=True)


      # Create a vertical scrollbar and associate it with the text widget
      scrollbar = tkinter.Scrollbar(self.middle_frame, command=self.api_response_text.yview)
      scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
      self.api_response_text.config(yscrollcommand=scrollbar.set)


      # Create a button to retrieve the user's prompt
      get_answer_button = tkinter.Button(self.button_frame, text="Get Answer", command=self.get_prompt, height=2,
                                         width=15, font=("Helvetica", 14, "bold"))
      get_answer_button.pack(side='left')


      # Create button to view conversation log
      view_log_button = tkinter.Button(self.button_frame, text="View Conversation Log", command=self.view_log,
                                       height=2, width=20, font=("Helvetica", 14, "bold"))
      view_log_button.pack(side='right')


      # Create button Exit GUI
      exit_button = tkinter.Button(self.bottom_frame, text='EXIT', command=self.main_window.destroy, height=2,
                                   width=15, font=("Helvetica", 14, "bold"))
      exit_button.pack()


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
          # Display an error message when the entry is empty
          error_message = "Error: Please enter a question."
          self.display_response(error_message, is_error=True)
          return


      try:
          # Call functions for further processing, e.g., insert into the database
          api_response = self.generate_response(prompt)


          # Update the GUI with the API response
          self.display_response(api_response)


          # Insert the conversation into the database
          self.insert_level1_conversation(prompt, api_response)
      except Exception as e:
          # Handle any unexpected errors during processing
          error_message = f"Error: An unexpected error occurred - {str(e)}"
          self.display_response(error_message, is_error=True)




  def insert_level1_conversation(self, prompt, response):
      # Create connection to SQLite server
      conn = sqlite3.connect('conversation.db')
      cursor = conn.cursor()


      cursor.execute('''INSERT INTO level1 (prompt, response)
                     VALUES (?, ?)''', (prompt, response))


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
          max_tokens=100
      )
      return response.choices[0].text.strip()




  def display_response(self, response, is_error=False):
      # Update the text in the API response widget
      self.api_response_text.delete("1.0", tkinter.END)  # Clear previous content
      self.api_response_text.insert(tkinter.END, response)


      # Update the StringVar for displaying the API response
      if is_error:
          response = f"ERROR: {response}"


      self.output_var.set(response)




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





if __name__ == "__main__":
  blackbox = BlackBox()





