<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro de Atividades</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 14px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        .hidden {
            display: none;
        }
        #resultado {
            margin-top: 20px;
            padding: 15px;
            background-color: #e8f5e9;
            border-radius: 5px;
            color: #2e7d32;
            font-weight: 500;
        }
        .error {
            color: #d32f2f;
            font-size: 14px;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Registro de Atividades</h1>
        
        <div class="form-group">
            <label for="matricula">Matrícula do Usuário:</label>
            <input type="text" id="matricula" placeholder="Digite sua matrícula" maxlength="10">
            <div id="matriculaError" class="error hidden"></div>
        </div>
        
        <div class="form-group">
            <label for="atividade">Atividade Executada:</label>
            <select id="atividade">
                <option value="">Selecione uma atividade</option>
                <option value="Cabide">Cabide</option>
                <option value="Runner">Runner</option>
                <option value="Descargar de caminhão">Descargar de caminhão</option>
                <option value="outros">Outros</option>
            </select>
            <div id="atividadeError" class="error hidden"></div>
        </div>
        
        <div id="outrosContainer" class="form-group hidden">
            <label for="outrosTexto">Especifique a atividade:</label>
            <input type="text" id="outrosTexto" placeholder="Digite a atividade realizada">
            <div id="outrosError" class="error hidden"></div>
        </div>
        
        <button id="registrarBtn">Registrar Atividade</button>
        
        <div id="resultado" class="hidden"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const atividadeSelect = document.getElementById('atividade');
            const outrosContainer = document.getElementById('outrosContainer');
            const outrosTexto = document.getElementById('outrosTexto');
            const registrarBtn = document.getElementById('registrarBtn');
            const resultadoDiv = document.getElementById('resultado');

            // Mostrar campo "Outros" quando selecionado
            atividadeSelect.addEventListener('change', function() {
                if (this.value === 'outros') {
                    outrosContainer.classList.remove('hidden');
                } else {
                    outrosContainer.classList.add('hidden');
                }
            });

            // Registrar atividade
            registrarBtn.addEventListener('click', function() {
                const matricula = document.getElementById('matricula').value.trim();
                const atividade = atividadeSelect.value;
                const outros = outrosTexto.value.trim();
                
                // Reset errors
                document.querySelectorAll('.error').forEach(el => {
                    el.classList.add('hidden');
                });
                
                // Validações
                let isValid = true;
                
                if (!matricula) {
                    document.getElementById('matriculaError').textContent = 'Por favor, digite a matrícula';
                    document.getElementById('matriculaError').classList.remove('hidden');
                    isValid = false;
                }
                
                if (!atividade) {
                    document.getElementById('atividadeError').textContent = 'Por favor, selecione uma atividade';
                    document.getElementById('atividadeError').classList.remove('hidden');
                    isValid = false;
                }
                
                if (atividade === 'outros' && !outros) {
                    document.getElementById('outrosError').textContent = 'Por favor, especifique a atividade';
                    document.getElementById('outrosError').classList.remove('hidden');
                    isValid = false;
                }
                
                if (!isValid) return;
                
                // Montar resultado
                const atividadeFinal = atividade === 'outros' ? outros : atividade;
                const registro = `
                    <strong>Registro realizado com sucesso!</strong><br><br>
                    <strong>Matrícula:</strong> ${matricula}<br>
                    <strong>Atividade:</strong> ${atividadeFinal}<br>
                    <strong>Horário:</strong> ${new Date().toLocaleTimeString()}
                `;
                
                resultadoDiv.innerHTML = registro;
                resultadoDiv.classList.remove('hidden');
                
                // Limpar formulário
                document.getElementById('matricula').value = '';
                atividadeSelect.value = '';
                outrosContainer.classList.add('hidden');
                outrosTexto.value = '';
            });
        });
    </script>
</body>
</html>
