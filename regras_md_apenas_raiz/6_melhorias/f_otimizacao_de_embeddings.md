# Otimização de Embeddings

## Descrição
Melhoria no processo de geração e armazenamento de embeddings

## Implementação
```python
import gensim.models as gm

# Carregar o dataset
dataset = pd.read_csv('dataset.csv')

# Pré-processar o texto
dataset['text'] = dataset['text'].str.lower()
dataset['text'] = dataset['text'].str.replace('[^\w\s]', '')

# Criar o modelo de embeddings
model = gm.Word2Vec(dataset['text'], min_count=1)

# Salvar o modelo
model.save('word2vec.model')

# Carregar o modelo salvo
model = gm.Word2Vec.load('word2vec.model')

# Obter o vetor de embedding de uma palavra
word_embedding = model['palavra']
```
