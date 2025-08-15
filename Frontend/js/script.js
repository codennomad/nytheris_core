// Aguarda o conteúdo da página carregar completamente antes de executar o script
document.addEventListener('DOMContentLoaded', () => {

    // 1. Selecionando os Elementos do HTML
    const form = document.getElementById('shorten-form');
    const urlInput = document.getElementById('url-input');
    const optionsToggle = document.getElementById('options-toggle');
    const advancedOptions = document.getElementById('advanced-options');
    const resultSection = document.getElementById('result-section');
    const shortUrlOutput = document.getElementById('short-url-output');
    const copyButton = document.getElementById('copy-button');

    // 2. Lógica para mostrar/esconder opções avançadas
    optionsToggle.addEventListener('click', () => {
        if (advancedOptions.style.display === 'flex') {
            advancedOptions.style.display = 'none';
            optionsToggle.textContent = 'Opções Avançadas ↓';
        } else {
            advancedOptions.style.display = 'flex';
            optionsToggle.textContent = 'Opções Avançadas ↑';
        }
    });

    // 3. Lógica para lidar com o envio do formulário
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Previne o recarregamento da página

        // Montando o corpo (payload) da requisição para a nossa API
        const payload = {
            url: urlInput.value,
            custom_alias: document.getElementById('custom-alias').value || null,
            password: document.getElementById('password').value || null,
            max_clicks: parseInt(document.getElementById('max-clicks').value, 10) || 0
        };

        // Limpa campos opcionais que não foram preenchidos
        if (!payload.custom_alias) delete payload.custom_alias;
        if (!payload.password) delete payload.password;

        try {
            // 4. Fazendo a chamada para a nossa API FastAPI
            const response = await fetch('http://localhost:8000/api/v1/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                // Se a API retornar um erro (ex: apelido já em uso), exibe o alerta
                throw new Error(data.detail || 'Ocorreu um erro.');
            }

            // 5. Exibindo o resultado
            shortUrlOutput.value = data.short_url;
            resultSection.classList.remove('hidden');

        } catch (error) {
            // Exibe um alerta de erro para o usuário
            alert(`Erro ao encurtar a URL: ${error.message}`);
        }
    });

    // 6. Lógica do botão de copiar
    copyButton.addEventListener('click', () => {
        shortUrlOutput.select(); // Seleciona o texto no input
        navigator.clipboard.writeText(shortUrlOutput.value)
            .then(() => {
                copyButton.textContent = 'Copiado!';
                setTimeout(() => {
                    copyButton.textContent = 'Copiar';
                }, 2000); // Volta ao texto original após 2 segundos
            })
            .catch(err => {
                alert('Falha ao copiar o link.');
            });
    });
});