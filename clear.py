import sqlite3

# Connect to the database
conn = sqlite3.connect('C:\\Users\\habib\\OneDrive\\Desktop\\QuizGen\\quizgen.db')
c = conn.cursor()

# Delete all records from the scores table
c.execute("DELETE FROM scores")

# Commit the changes
conn.commit()

# Close the connection
conn.close()

print("Leaderboard data cleared successfully!")