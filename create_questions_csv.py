"""
create_questions_csv.py - Extract Kinyarwanda questions and create a CSV file with specified columns
"""

import csv
import os

def main():
    # Define the questions
    questions = [
        "Kubera iki mumaze igihe kinini mutaduha uburenganzira bwo gufungura Irembo ryacu? Ndashaka nanjye kujya mfasha abantu kubona serivisi z'Irembo",
        "Ese umuntu ashaka akazi mu Irembo yabavugisha gute?",
        "Icyangombwa cyanjye cy'ubutaka narakibuze kandi ngejeje igihe cyo gutanga umusoro, ubwo nakibona gute ngo mbashe kwishyura imisoro",
        "Ese ko mbona gusaba pasiporo bitari gukunda mwamfasha kuyinsabira",
        "Ese Irembo, iyo umuntu amaze kwiyandikisha kuri permit ntabone code yiwe biba byagenze gute ubwo?",
        "Aka message mwampaye narakabuze kandi ejo mfite examen. nakabona gute?",
        "Icyumweru gishize niyandikishije ku kizami ariko sinibuka italiki y'ikizamini. Munyibutse italiki",
        "Nijoro niyandikishije ariko ndi kwishyura bikanga. Kandi ndabishaka cyane mumfashe",
        "Nasabye icyemezo gisimbura indangamuntu ariko ntabwo nibuka numero yanjye ya dosiye. Mwanyibutsa?",
        "Ndikugerageza kudownloadinga icyemezo cyanjye cy'amavuko nk'ibisanzwe ariko ntibikunda sinzi ikibazo kirimo",
        "Maze kwiyandikisha ariko nsanze nashyizemo kuzakorera Rusizi kandi nashakaga Musanze. Munkuriremo iyo dosiye nongere niyandikishe",
        "Ese birashoboka ko mwampindurira uwo twari kuzashakana nkashyiraho undi. Nandikishije ishyingirwa ariko uwo twari kuzashakana yarabyanze nshaka undi",
        "Ndashaka kwishyura imisoro hakiri kare bataramfungira.",
        "Nabonye ku mbuga zanyu mwatumenyesheje ko mushobora kudufasha gusimbuza amafoto yo ku ndangamuntu, ndasabwa iki?",
        "Mu kwiyandikisha kuri permit, kuki buri gihe nsangamo imyanya yo muri Busanza gusa?",
        "Maze kwishyura Traffic fine ariko nsanga n'umushoferi wanjye nawe yishyuye, ubwo ayo mafaranga turayasubizwa bigenze gute?",
        "ko ubushize nasabye icyemezo cy'uko ntafunzwe nkahita nkibona, ubu bwo kuki cyatinze? kimaze icyumweru kirenga.",
        "Twasabye ibyemezo by'uko tutafunzwe njye na madamu n'umuhungu wanjye ariko bo barabibonye njye sinzi impamvu byatinze",
        "Nifuzaga kumenya aho icyangombwa cyanjye cy'ubutaka kigeze kuko twakoze mutation ukwezi gushize kandi sindabona icyangombwa cyanjye",
        "Mvuye mu kizamini ariko nahise nzimya machine ntabonye amanota yanjye, mwamfasha kuyamenya"
    ]
    
    # Define the CSV file headers
    headers = [
        "Question", 
        "Answer", 
        "Topic Category", 
        "gpt-4o fluency score *", 
        "gpt-03-mini fluency score *", 
        "gpt-01-preview fluency score *", 
        "claude-sonnet-3.7 fluency score *", 
        "claude-sonnet-3.5 fluency score *", 
        "grok-3 fluency score *", 
        "gemini-flash-2.0 fluency score *", 
        "google-translate"
    ]
    
    # Create and write to the CSV file
    csv_file_path = "kinyarwanda_questions.csv"
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write the headers
        writer.writerow(headers)
        
        # Write each question with empty cells for other columns
        for question in questions:
            # Create a row with the question and empty strings for other columns
            row = [question] + [""] * (len(headers) - 1)
            writer.writerow(row)
    
    print(f"CSV file created successfully: {csv_file_path}")
    print(f"Total questions: {len(questions)}")

if __name__ == "__main__":
    main()
