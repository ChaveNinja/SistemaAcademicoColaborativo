#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char nome[50];
    int codigo;
} Turma;

int main() {
    int qtd;
    FILE *arquivo;
    Turma turma;

    // Cria a pasta output (caso não exista)
    system("mkdir output");

    arquivo = fopen("output/turmas.txt", "w");
    if (arquivo == NULL) {
        printf("Erro ao criar arquivo!\n");
        return 1;
    }

    printf("Quantos grupo deseja cadastrar? ");
    scanf("%d", &qtd);

    for (int i = 0; i < qtd; i++) {
        printf("\n--- Grupo %d ---\n", i + 1);
        printf("Numero do Grupo: ");
        scanf("%d", &turma.codigo);
        printf("Nome da turma: ");
        getchar();
        fgets(turma.nome, sizeof(turma.nome), stdin);

        for (int j = 0; turma.nome[j]; j++) {
            if (turma.nome[j] == '\n') {
                turma.nome[j] = '\0';
                break;
            }
        }

        fprintf(arquivo, "%d,%s\n", turma.codigo, turma.nome);
    }

    fclose(arquivo);
    printf("\n✅ Arquivo 'turmas.txt' criado com sucesso em: output/turmas.txt\n");

    return 0;
}
