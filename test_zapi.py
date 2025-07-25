from src.crewai_sellers_flow.adapters.whatsapp_lka_sharepoint import WhatsappLKASharepoint
from src.crewai_sellers_flow.adapters.api_z_message import ApiZMessage
import base64

def convert_to_base64(file_path: str):
    with open(file_path, "rb") as file:
        file_data = file.read()
        base64_string = base64.b64encode(file_data).decode('utf-8')    
    return base64_string

if __name__ == "__main__":
    # sharepoint = WhatsappLKASharepoint()
    # lka = sharepoint.get_lka(10118)

    api_z_message = ApiZMessage()
    # response = api_z_message.send_message(
    #     5551998590811,
    #     # "Oi Parceiro, alguns pedidos da sua loja estão sendo cancelados com a justificativa de “Problemas na Operação”. Pensando em melhorar cada vez mais sua operação e para não perder pedidos, prepare o seu time para evitar essas situações, ative no Seu.Zé apenas os itens que você realmente tem em estoque e se organize sua equipe de motocas para evitar atrasos. Você pode entender quais são seus horários de picos com o relatório semanal que te enviamos.",
    #     # "Olá, parceiro. Sua taxa de aceitação de pedidos está superior a 94%, nível adequado que demonstra o empenho em oferecer um ótimo serviço. Seu resultado semanal foi de 97.20% Continue seguindo as boas práticas de atendimento e evitando cancelamentos. Se tiver alguma dificuldade em concluir pedidos, entre em contato para encontrarmos uma solução juntos! Atenção ao Sábado as 20h. Cancelamento é FALTA GRAVE.",
    #     "Muitos pedidos da sua loja estão sendo cancelados com a justificativa de “Falta de Produtos”. Ative no Seu.Zé apenas os itens que você realmente tem em estoque e em quantidade suficiente. Mantenha o estoque SEMPRE atualizado ao longo da operação. Confira a lista de produtos do seu portfólio ideal no Seu.Zé em: 'Estoque de Produtos' > 'Portfólio Ideal.",
    #     "3DC54E6DCAACB064BEB44E46D4B53ED3",
    #     "A2BDE7912126B13D4617DE9D",
    # )
    # print(response)
    # base64_string = convert_to_base64("downloads/imagem_completa.png")
    # base64_string = convert_to_base64("downloads/Cancelamentos Loja.png")
    # response = api_z_message.send_image(
    #     5551998590811,
    #     f"data:image/png;base64,{base64_string}",
    #     "3DC54E6DCAACB064BEB44E46D4B53ED3",
    #     "A2BDE7912126B13D4617DE9D",
    # )
    # response = api_z_message.send_message(
    #     5551998590811,
    #     # "Oi Parceiro, alguns pedidos da sua loja estão sendo cancelados com a justificativa de “Problemas na Operação”. Pensando em melhorar cada vez mais sua operação e para não perder pedidos, prepare o seu time para evitar essas situações, ative no Seu.Zé apenas os itens que você realmente tem em estoque e se organize sua equipe de motocas para evitar atrasos. Você pode entender quais são seus horários de picos com o relatório semanal que te enviamos.",
    #     # "Olá, parceiro. Sua taxa de aceitação de pedidos está superior a 94%, nível adequado que demonstra o empenho em oferecer um ótimo serviço. Seu resultado semanal foi de 97.20% Continue seguindo as boas práticas de atendimento e evitando cancelamentos. Se tiver alguma dificuldade em concluir pedidos, entre em contato para encontrarmos uma solução juntos! Atenção ao Sábado as 20h. Cancelamento é FALTA GRAVE.",
    #     "⚠️ *ALTO ÍNDICE DE CANCELAMENTO DE PEDIDOS* ⚠️\n\nMuitos pedidos da sua loja estão sendo cancelados com a justificativa de “Falta de Produtos”. Ative no Seu.Zé apenas os itens que você realmente tem em estoque e em quantidade suficiente. Mantenha o estoque SEMPRE atualizado ao longo da operação. Confira a lista de produtos do seu portfólio ideal no Seu.Zé em: 'Estoque de Produtos' > 'Portfólio Ideal.\n\n *Atenção a Sexta-feira as 19h.*\nCancelamento é FALTA GRAVE.\n\n Equipe Zé Delivery",
    #     "3DC54E6DCAACB064BEB44E46D4B53ED3",
    #     "A2BDE7912126B13D4617DE9D",
    # )

    # base64_string = convert_to_base64("downloads/Parabéns.png")
    # response = api_z_message.send_image(
    #     5551998590811,
    #     f"data:image/png;base64,{base64_string}",
    #     "3DC54E6DCAACB064BEB44E46D4B53ED3",
    #     "A2BDE7912126B13D4617DE9D",
    # )
    response = api_z_message.send_message(
        5551998590811,
        # "Oi Parceiro, alguns pedidos da sua loja estão sendo cancelados com a justificativa de “Problemas na Operação”. Pensando em melhorar cada vez mais sua operação e para não perder pedidos, prepare o seu time para evitar essas situações, ative no Seu.Zé apenas os itens que você realmente tem em estoque e se organize sua equipe de motocas para evitar atrasos. Você pode entender quais são seus horários de picos com o relatório semanal que te enviamos.",
        # "Olá, parceiro. Sua taxa de aceitação de pedidos está superior a 94%, nível adequado que demonstra o empenho em oferecer um ótimo serviço. Seu resultado semanal foi de 97.20% Continue seguindo as boas práticas de atendimento e evitando cancelamentos. Se tiver alguma dificuldade em concluir pedidos, entre em contato para encontrarmos uma solução juntos! Atenção ao Sábado as 20h. Cancelamento é FALTA GRAVE.",
        "🎉 *PARABÉNS* 🎉\n\nOlá, parceiro. Sua taxa de aceitação de pedidos está superior a 94%, nível adequado que demonstra o empenho em oferecer um ótimo serviço. Seu resultado semanal foi de 95.8% Continue seguindo as boas práticas de atendimento e evitando cancelamentos. Se tiver alguma dificuldade em concluir pedidos, entre em contato para encontrarmos uma solução juntos!\n\n *Atenção ao Sábado as 20h.*\nCancelamento é FALTA GRAVE.\n\n Equipe Zé Delivery",
        "3DC5654094757038A9DE96155CBF9532",
        "3918512C84B2158BC52FB12B",
    )    
    print(response)
