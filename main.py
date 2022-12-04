"""
    GPT-3 Implementation as a DocumentCloud Add-on
"""

import csv, re, time, os, openai
from documentcloud.addon import AddOn

openai.api_key = os.environ["TOKEN"]

class GPTPlay(AddOn):    
    def main(self):
        documents = []
        # provide at least one document.
        if self.documents:
            self.set_message("Running analysis on selected documents.")
            for document in self.documents:
                documents.append(str(document))
        else:
            self.set_message("Running analysis on search results.")
            search_results = self.client.documents.search(self.query)
            for document in search_results:
                documents.append(str(document.id))
        
        if self.get_documents(): # Check to make sure there are documents:
            with open("compared_docs.csv", "w+") as file_:
                writer = csv.writer(file_)
                writer.writerow(
                    ["document_title", "url", "text", "output"]
                )
                user_input = self.data.get("prompt").translate(str.maketrans({"-":  r"\-",
                                              "]":  r"\]",
                                              "\\": r"\\",
                                              "^":  r"\^",
                                              "$":  r"\$",
                                              "*":  r"\*",
                                              ".":  r"\."})) 

                for document in self.get_documents():
                    print("Beginning document iteration.")
                    try:
                        # Just starting with page one for now due to API limits.
                        full_text = document.get_page_text(1).translate(str.maketrans({"-":  r"\-", 
                                              "]":  r"\]",
                                              "\\": r"\\",
                                              "^":  r"\^",
                                              "$":  r"\$",
                                              "*":  r"\*",
                                              ".":  r"\."})) 
                        submission="%s\n=========\n%s=========="%(user_input, full_text)
                        response = openai.Completion.create(
                            model="text-davinci-002",
                            prompt=submission,
                            temperature=0.7,
                            max_tokens=1000,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                            )
                        results = response.choices[0].text
#                        print(results)
                        writer.writerow(
                        [document.title, "url", "text", "output"]
                        )
                        writer.writerow([document.title, document.canonical_url, full_text, results])

                    except:
                        print("Error, moving on to the next item.")
                self.upload_file(file_)
        else:
            self.set_message("It looks like no documents were selected. Search for some or select them and run again.")



if __name__ == "__main__":
    GPTPlay().main()
