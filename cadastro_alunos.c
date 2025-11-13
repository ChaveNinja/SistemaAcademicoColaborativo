#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char matricula[20];
    char nome[50];
    float np1, np2, pim, media;
    int cod_turma;
} Aluno;

int main() {
    int qtd;
    FILE *arquivo;
    Aluno aluno;

    system("mkdir output");

    arquivo = fopen("output/alunos.txt", "w");
    if (arquivo == NULL) {
        printf("Erro ao criar arquivo!\n");
        return 1;
    }

    printf("Quantos alunos deseja cadastrar? ");
    while (scanf("%d", &qtd) != 1) {
        printf("Por favor, insira um numero inteiro valido: ");
        while(getchar() != '\n'); // limpa buffer
    }

    for (int i = 0; i < qtd; i++) {
        printf("\n--- Aluno %d ---\n", i + 1);

        printf("Numero do Grupo: ");
        while (scanf("%d", &aluno.cod_turma) != 1) {
            printf("Por favor, insira um numero inteiro valido: ");
            while(getchar() != '\n');
        }

        getchar(); // remove \n do buffer
        printf("Matricula do Aluno: ");
        fgets(aluno.matricula, sizeof(aluno.matricula), stdin);
        for (int j = 0; aluno.matricula[j]; j++) {
            if (aluno.matricula[j] == '\n') {
                aluno.matricula[j] = '\0';
                break;
            }
        }

        printf("Nome do aluno: ");
        fgets(aluno.nome, sizeof(aluno.nome), stdin);
        for (int j = 0; aluno.nome[j]; j++) {
            if (aluno.nome[j] == '\n') aluno.nome[j] = '\0';
        }

        printf("Nota NP1: ");
        while (scanf("%f", &aluno.np1) != 1) {
            printf("Por favor, insira um número valido: ");
            while(getchar() != '\n');
        }

        printf("Nota NP2: ");
        while (scanf("%f", &aluno.np2) != 1) {
            printf("Por favor, insira um numero valido: ");
            while(getchar() != '\n');
        }

        printf("Nota PIM: ");
        while (scanf("%f", &aluno.pim) != 1) {
            printf("Por favor, insira um numero valido: ");
            while(getchar() != '\n');
        }

        aluno.media = (aluno.np1 * 0.4f) + (aluno.np2 * 0.4f) + (aluno.pim * 0.2f);

        fprintf(arquivo, "%d,%s,%s,%.2f,%.2f,%.2f,%.2f\n",
                aluno.cod_turma, aluno.matricula, aluno.nome, aluno.np1, aluno.np2, aluno.pim, aluno.media);
    }

    fclose(arquivo);
    printf("\nArquivo 'alunos.txt' criado com sucesso em: output/alunos.txt\n");

    return 0;
}
