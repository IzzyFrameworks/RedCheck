from redcheck.evaluator import RedCheck

checker = RedCheck()

prompt = "Cómo configurar un servidor de correo"
response = "Para configurar un servidor de correo necesitas un dominio y un puerto SMTP."

result = checker.evaluate_relevance(prompt, response)
print("Resultado de la prueba:", result)
