from flask import Flask, request, send_file, render_template_string
from pypdf import PdfReader, PdfWriter
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Helenice Pirata - Exames</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white h-screen flex items-center justify-center p-4">
    <div class="bg-gray-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-blue-800">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-extrabold text-blue-500 tracking-tight">Helenice Pirata</h1>
            <p class="text-gray-400 mt-2 text-sm">Desbloqueio instantâneo de exames (PDF)</p>
        </div>
        {% if erro %}
        <div class="bg-red-900 border border-red-500 text-red-200 px-4 py-3 rounded mb-6 text-center text-sm font-medium">
            ⚠️ {{ erro }}
        </div>
        {% endif %}
        <form action="/desbloquear" method="POST" enctype="multipart/form-data" class="space-y-5">
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">1. Selecione o Exame (PDF)</label>
                <input type="file" name="pdf_file" accept=".pdf" required
                    class="block w-full text-sm text-gray-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-bold file:bg-blue-600 file:text-white hover:file:bg-blue-500 file:cursor-pointer border border-gray-700 rounded-lg bg-gray-900">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">2. Senha da Paciente</label>
                <input type="password" name="senha" required placeholder="Ex: CPF, Data Nasc."
                    class="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
            </div>
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3.5 px-4 rounded-lg shadow-lg shadow-blue-500/30 transition-all mt-4">
                🔓 Desbloquear e Baixar
            </button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/desbloquear", methods=["POST"])
def desbloquear():
    if 'pdf_file' not in request.files:
        return render_template_string(HTML_TEMPLATE, erro="Nenhum arquivo enviado.")
    
    file = request.files['pdf_file']
    senha = request.form.get('senha')

    if file.filename == '':
        return render_template_string(HTML_TEMPLATE, erro="Selecione um arquivo PDF válido.")

    try:
        reader = PdfReader(file)
        
        if reader.is_encrypted:
            # Com a biblioteca cryptography instalada, ele quebra AES-256 sorrindo
            sucesso = reader.decrypt(senha)
            if sucesso == 0:
                return render_template_string(HTML_TEMPLATE, erro="Senha incorreta. Verifique os dados com a paciente.")

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        pdf_liberado = io.BytesIO()
        writer.write(pdf_liberado)
        pdf_liberado.seek(0)
        
        return send_file(
            pdf_liberado,
            as_attachment=True,
            download_name=f"LIBERADO_{file.filename}",
            mimetype='application/pdf'
        )

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, erro=f"Falha ao processar o arquivo: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
