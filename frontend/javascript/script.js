const inputMg = document.querySelector('#arq-mg');
const inputController = document.querySelector('#arq-controller');
const btnEnviar = document.querySelector('#enviar');

btnEnviar.addEventListener('click', async () =>{
    const arqMg = inputMg.files[0];
    const arqController = inputController.files[0];

    if(!arqController || !arqMg){
        alert('Um dos arquivos não foi importado, favor revisar!');
        return;
    }

    const formData = new FormData();

    formData.append("arquivo_mg", arqMg);
    formData.append("arquivo_controller", arqController);

    try{
        const response = await fetch(
            "http://localhost:8000/processar", 
            {
                method: "POST",
                body: formData
            }
        );
        if(!response.ok){
            throw new Error("Erro ao processar arquivos");
        }
        
        const resultado = await response.json();
        console.log(resultado)

    } catch (erro) {
        console.error(erro);
        alert('Não foi possível enviar arquivos')
    }
});