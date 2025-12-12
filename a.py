import google.generativeai as genai

# Replace with your API key
genai.configure(api_key="AIzaSyCLaEyrOgZGax73p9OYehQCChtzug_Xoww")

try:
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content("Hello! Say 'API working' if you can read this.")
    print(response.text)
except Exception as e:
    print("Error:", e)
