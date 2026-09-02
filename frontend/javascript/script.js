const inputMg = document.querySelector('#arq-mg');
const inputController = document.querySelector('#arq-controller');
const btnEnviar = document.querySelector('#enviar');
const url = 'http://localhost:8000'

async function enviarPlanilhas(url, arqMg, arqController){
    const formData = new FormData();
    formData.append("arquivo_mg", arqMg);
    formData.append("arquivo_controller", arqController);

    const response = await fetch(url, {
        method: "POST",
        body: formData
    });

    if (!response.ok){
        const corpoErro = await response.json();
        const erro = new Error("Falha na requisição");
        erro.status = response.status;
        erro.detail = corpoErro.detail.Error
        throw erro;
    }

    return response.json();
}

function reportarErro(etapa, erro){
    console.error(`Erro na etapa "${etapa}": `, erro);
    if (erro.detail){
        console.error("Detalhes:", erro.detail);
    }
    alert(`Não foi possível concluir "${etapa}". Veja o console para detalhes.`)
}

btnEnviar.addEventListener('click', async () =>{
    const arqMg = inputMg.files[0];
    const arqController = inputController.files[0];

    if(!arqController || !arqMg){
        alert('Um dos arquivos não foi importado, favor revisar!');
        return;
    }

    let layoutOk

    try{
        layoutOk = await enviarPlanilhas(
            `${url}/validar_layout`,
            arqMg,
            arqController
        );
        console.log('Layout validado:', layoutOk);

    } catch (erro) {
        reportarErro('validação de layout', erro);
        return;
    }

    try {
        const resultadoFinal = await enviarPlanilhas(
            `${url}/processar`,
            arqMg,
            arqController
        );
        console.log('Processamento concluido:', resultadoFinal);

    } catch (erro) {
        reportarErro('processamento', erro)
    }

});