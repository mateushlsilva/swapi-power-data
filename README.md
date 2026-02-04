# SWAPI Power Data API 🚀

Este projeto é uma API de alta performance desenvolvida com **FastAPI**, integrada ao **Redis** para cache e ao **Google Firestore** para persistência de dados. O projeto foi desenhado seguindo princípios de arquitetura escalável e está totalmente containerizado.

## 🛠 Tecnologias Utilizadas

* **FastAPI**: Framework web assíncrono de alta performance.
* **Redis**: Camada de cache para otimização de consultas.
* **Google Firestore**: Banco de dados NoSQL escalável.
* **Docker & Docker Compose**: Orquestração de ambiente de desenvolvimento.

---

## 🏗 Arquitetura e Decisões Técnicas

A API foi projetada para ser *stateless*, permitindo o escalonamento horizontal em ambientes de nuvem como o **Google Cloud Run**.

### 1. Persistência e Emulação

Para garantir a fidelidade entre os ambientes de desenvolvimento e produção, utilizei o **Firestore Emulator**.

* **Ambiente Local**: A API detecta a variável `FIRESTORE_EMULATOR_HOST` e desvia o tráfego para o container local.
* **Ambiente de Produção**: O SDK do Google utiliza automaticamente o *Application Default Credentials* (ADC) para conectar ao recurso nativo da GCP.

### 2. Camada de Cache

O **Redis** é utilizado para reduzir a latência em rotas de leitura pesada. No ambiente Docker, a comunicação ocorre via rede interna; em produção, a conectividade é garantida via **Serverless VPC Access Connector**.



### 3. Circuit Breaker 
Para garantir que a API continue operando mesmo em caso de instabilidade de serviços externos (como a API pública da SWAPI), implementei:

Circuit Breaker: Mecanismo que "abre o circuito" ao detectar falhas consecutivas em integrações externas, impedindo que falhas em cascata sobrecarreguem a aplicação e permitindo respostas rápidas de erro ou uso de dados em cache.

---

## 🚀 Como Rodar o Projeto Localmente

1. **Clone o repositório:**
```bash
git clone https://github.com/mateushlsilva/swapi-power-data.git
cd swapi-power-data
```


2. **Configure as variáveis de ambiente:**
Crie um arquivo `.env` baseado no exemplo abaixo:
```env
REDIS=
FIRESTORE_EMULATOR_HOST=
GOOGLE_CLOUD_PROJECT=
JWT_SECRET_KEY=
SWAPI_BASE=https://swapi.dev/api/
```


3. **Suba os containers:**
```bash
docker compose up --build
```


4. **Acesse a documentação:**
Abra o navegador em `http://localhost:8000/docs`.

---

## 📝 Notas de Desenvolvimento

* **Resiliência**: O código implementa padrões de reconexão assíncrona para o Redis e Firestore durante o `lifespan` da aplicação.
* **Performance**: Utilização de `FieldFilter` otimizado para consultas no Firestore, evitando *warnings* de performance e garantindo compatibilidade com versões futuras do SDK.

---

### ⚠️ Notas sobre o Deploy (GCP)

Originalmente, este projeto foi desenhado para ser implantado no **Google Cloud Platform (GCP)** utilizando **Cloud Run**, **Cloud Memorystore (Redis)** e **Cloud Firestore**.

No entanto, o deploy em ambiente de produção não pôde ser concluído devido a uma restrição administrativa na console do Google Cloud (**Erro: [OR_BACR2_44]**), que resultou em um bloqueio preventivo da conta de faturamento (Billing), impedindo o provisionamento de recursos gerenciados como o conector VPC e a instância de Redis.

**Para contornar essa limitação e garantir a entrega funcional do desafio:**

* O ambiente foi totalmente emulado utilizando **Docker Compose**, replicando a topologia de rede e o comportamento dos serviços cloud.
* A lógica de conexão no arquivo `lifespan.py` foi mantida de forma dinâmica, preparada para alternar automaticamente para os serviços nativos da GCP assim que as credenciais e o ambiente estiverem normalizados.
* O código foi validado localmente garantindo que a comunicação entre os containers utilize os mesmos protocolos que seriam usados em produção.

---

### 🧑‍💻 Autor

**Mateus Silva**