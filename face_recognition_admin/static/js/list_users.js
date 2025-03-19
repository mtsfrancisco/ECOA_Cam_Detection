function deleteUser(userId) {
    if (confirm("Tem certeza que deseja excluir este usuário?")) {
        fetch("{% url 'delete_user' 0 %}".replace("0", userId), { method: "POST" }) // Caminho relativo ao root
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(error => alert("Erro ao excluir usuário: " + error));
    }
}