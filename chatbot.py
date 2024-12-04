import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import re
import random

class HumanLikeLegalChatbot:
    def __init__(self, csv_path, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the conversational legal AI assistant.
        """
        try:
            # Load CSV
            self.df = pd.read_csv(csv_path, low_memory=False)
            
            # Prepare conversational templates
            self.prepare_conversation_templates()
            
            # Prepare searchable data
            self.prepare_data()
            
            # Load AI model
            print("Preparing legal knowledge base... 📚")
            self.model = SentenceTransformer(model_name)
            
            # Create embeddings
            self.create_embeddings()
            
        except Exception as e:
            print(f"Initialization Error: {e}")
            raise
    
    def prepare_conversation_templates(self):
        """
        Prepare conversational response templates.
        """
        self.opening_phrases = [
            "Let me break this down for you...",
            "Here's what I found in the legal records...",
            "Based on the available legal information...",
            "Diving into the legal specifics...",
        ]
        
        self.context_phrases = [
            "It's important to understand that...",
            "From a legal perspective...",
            "The law is quite clear on this matter...",
            "Legally speaking...",
        ]
        
        self.conclusion_phrases = [
            "To sum up the legal implications...",
            "In essence, the key takeaway is...",
            "Let me recap the critical points...",
            "Here's what you need to know...",
        ]
    
    def prepare_data(self):
        """
        Prepare the dataframe for semantic search and convert numeric columns.
        """
        # Convert numeric columns
        numeric_columns = ['fo_max_years', 'fo_max_fine']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Existing search text preparation
        search_columns = [
            'short_title', 
            'subject_matter_name', 
            'offence_title', 
            'offence_description'
        ]
        
        available_columns = [col for col in search_columns if col in self.df.columns]
        
        self.df['combined_search_text'] = self.df[available_columns].fillna('').agg(' '.join, axis=1)
        
        self.df['combined_search_text'] = self.df['combined_search_text'].apply(
            lambda x: re.sub(r'\s+', ' ', str(x).lower().strip())
        )
    
    def create_embeddings(self):
        """Create semantic embeddings for search texts."""
        self.embeddings = self.model.encode(
            self.df['combined_search_text'].tolist(),
            convert_to_tensor=True
        )
    
    def get_relevant_laws(self, query, threshold=0.5, top_k=3):
        """
        Find relevant laws using semantic similarity.
        """
        query_embedding = self.model.encode(
            query.lower(),
            convert_to_tensor=True
        )
        
        with torch.no_grad():
            similarities = cosine_similarity(
                query_embedding.cpu().numpy().reshape(1, -1),
                self.embeddings.cpu().numpy()
            )[0]
        
        top_indices = np.argsort(similarities)[::-1]
        
        relevant_indices = [
            idx for idx in top_indices 
            if similarities[idx] >= threshold
        ][:top_k]
        
        return relevant_indices, similarities[relevant_indices]
    
    def generate_human_response(self, row, score):
        """
        Generate an AI-enhanced conversational response with better context and flow.
        """
        # Enhanced conversation starters based on confidence score
        high_confidence_starters = [
            "I'm quite confident I can help you with this.",
            "I've found some very relevant legal information for you.",
            "Let me share some important legal insights about this.",
        ]
        medium_confidence_starters = [
            "I've found some information that might help answer your question.",
            "Based on my analysis, here's what I understand about your query.",
            "Let me share what I've found in the legal documents.",
        ]
        low_confidence_starters = [
            "While this might not be exactly what you're looking for,",
            "I found some potentially relevant information,",
            "Here's what I could find that might be helpful,",
        ]

        # Select appropriate starter based on confidence score
        if score > 0.7:
            opening = random.choice(high_confidence_starters)
        elif score > 0.5:
            opening = random.choice(medium_confidence_starters)
        else:
            opening = random.choice(low_confidence_starters)

        # Context phrases based on subject matter
        subject_context = {
            'Financial Laws': [
                "In the realm of financial regulations,",
                "When it comes to financial matters,",
                "Under financial law provisions,"
            ],
            'Criminal Laws': [
                "In criminal justice matters,",
                "Under criminal law provisions,",
                "From a criminal law perspective,"
            ],
            # Add more subjects as needed
        }

        # Get contextual phrase based on subject matter
        subject_phrase = random.choice(
            subject_context.get(
                row['subject_matter_name'],
                ["According to the relevant legislation,"]
            )
        )

        # Build enhanced response
        response = f"{opening}\n\n{subject_phrase} "
        
        # Add main content with better natural language
        response += (
            f"the {row['short_title']} provides specific guidance on this matter. "
            f"This legislation specifically addresses {row['offence_title'].lower()}. "
            f"{row['offence_description'].lower()} "
        )

        # Add severity indicators and consequences
        severity_phrases = {
            (5, 500000): "This is considered a serious offense",
            (3, 300000): "This is treated as a significant violation",
            (1, 100000): "This is classified as a regulatory infraction"
        }

        severity_phrase = "This is treated as a legal violation"
        for (years, fine) in severity_phrases.keys():
            if (pd.notna(row.get('fo_max_years')) and row['fo_max_years'] >= years) or \
               (pd.notna(row.get('fo_max_fine')) and row['fo_max_fine'] >= fine):
                severity_phrase = severity_phrases[(years, fine)]
                break

        # Add punishment information with natural language
        if pd.notna(row.get('fo_max_years')) or pd.notna(row.get('fo_max_fine')):
            response += f"\n\n{severity_phrase}. Under the law, "
            penalties = []
            
            if pd.notna(row.get('fo_max_years')):
                year_word = "year" if row['fo_max_years'] == 1 else "years"
                penalties.append(f"imprisonment for up to {row['fo_max_years']} {year_word}")
            
            if pd.notna(row.get('fo_max_fine')):
                penalties.append(f"monetary penalties reaching ₹{row['fo_max_fine']}")
            
            if penalties:
                response += "the consequences may include " + " and ".join(penalties) + "."

        # Add contextual disclaimer based on confidence score
        if score > 0.8:
            disclaimer = (
                "\n\n⚖️ While I'm confident in this interpretation, please note that "
                "legal matters can be complex. It's advisable to consult with a legal "
                "professional for specific guidance tailored to your situation."
            )
        else:
            disclaimer = (
                "\n\n⚖️ Please note that this information is for general guidance only. "
                "Given the complexity of legal matters, it's essential to consult with "
                "a qualified legal professional for advice specific to your circumstances."
            )

        response += disclaimer
        
        return response
    
    def get_response(self, query):
        """Generate conversational response for user's query."""
        relevant_indices, scores = self.get_relevant_laws(query)
        
        if not relevant_indices:
            return (
                "I apologize, but I couldn't find specific legal information "
                "matching your query. Could you rephrase or provide more details? 🤔"
            )
        
        # Combine responses for multiple matches
        full_response = ""
        for idx, score in zip(relevant_indices, scores):
            row = self.df.iloc[idx]
            full_response += self.generate_human_response(row, score) + "\n\n" + "-"*50 + "\n\n"
        
        return full_response
    
    def chat(self):
        """Interactive conversational legal assistant."""
        print("\n⚖️ AI Legal Companion")
        print("I'm here to help you understand legal matters.")
        print("Ask about laws, offences, or legal implications.")
        print("Type 'quit' to exit. 👋")
        print("-" * 50)

        greetings = ['hi', 'hello', 'hey', 'greetings', 'howdy']
        
        while True:
            try:
                user_input = input("\n🗣️ Your legal query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Thank you for consulting me. Stay legally informed! 👨‍⚖️")
                    break

                if user_input in greetings:
                    print("\n🤖 Hello! How can I assist you with legal matters today?")
                    continue
                
                response = self.get_response(user_input)
                print("\n" + response)
                
            except Exception as e:
                print(f"🚨 Oops! An error occurred: {e}")

def main():
    # Path to your CSV file
    CSV_PATH = 'legal_database.csv'
    
    try:
        chatbot = HumanLikeLegalChatbot(CSV_PATH)
        chatbot.chat()
    except Exception as e:
        print(f"🚨 Failed to initialize legal assistant: {e}")

if __name__ == "__main__":
    main()