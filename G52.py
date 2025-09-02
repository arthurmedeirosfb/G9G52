import pulp
import pandas as pd

#leitura de dados -----------------------------
dt = pd.read_excel("data.ods",sheet_name="G52") #matriz do indice i
df_dist = pd.read_excel("data.ods", sheet_name="distanciaG52") #matriz de distancias

# dicionário de demanda
demand = {row['cidade']: row['indiceI'] for _, row in dt.iterrows()}
#print("Índice de Recife:", demand["Recife"])
#print("Índice de Salvador:", demand["Salvador"])

# dicionário das distancias[(cidade, cd)]
dist = {}
for _, row in df_dist.iterrows():
    cd = row['CD']
    for city in df_dist.columns[2:]:  # ignora ID e CD
        dist[(city, cd)] = row[city]

# CDs candidatos
candidates = ['recife', 'salvador']

# custos fixos de instalação (coloquei 0 pq os custos serão muito proximos em cada um, entao isso nao afetará o resultado)
#salvador custo m² FipeZAP: 7.647
#recife custo m² FipeZAP: 8.293
fixed_cost = {'recife': 0, 'salvador': 0}


#criacao do modelo ----------------------------
model = pulp.LpProblem("FacilityLocation", pulp.LpMinimize)

#criacao das variaveis ------------------------
y = pulp.LpVariable.dicts('Open', candidates, cat='Binary')  # abrir CD

transport_cost = []
for city, d in demand.items():
    for cd in candidates:
        transport_cost.append(d * dist[(city, cd)] * y[cd])

model += pulp.lpSum(fixed_cost[c] * y[c] for c in candidates) + pulp.lpSum(transport_cost)

# Restrição: abrir exatamente 1 CD: y0 + y1 = 1
model += pulp.lpSum(y[c] for c in candidates) == 1


#nao coloquei restricao de qual CD vai atender qual destino, pois so tem um CD.
#Mas se tivesse mais de um CD eu criaria uma variavel xij  


model.solve(pulp.PULP_CBC_CMD(msg=0))

print("Status:", pulp.LpStatus[model.status])
for c in candidates:
    print(f"{c}: {pulp.value(y[c])}")

print("Custo total:", pulp.value(model.objective))


