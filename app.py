from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DCJI3489CJ48JCN894JF8J3C81DH133E!d!#d24R$f#g@G#$g%$&'

# Coeficientes térmicos e propriedades (exemplos simplificados)
MATERIAIS = {
    "Tijolo Comum": {"conducao": 0.72, "convencao": 0.05, "radiacao": 0.9},
    "Refratário": {"conducao": 0.3, "convencao": 0.04, "radiacao": 0.8},
    "Bloco de Cimento": {"conducao": 0.9, "convencao": 0.06, "radiacao": 0.85},
    "Dry-wall": {"conducao": 0.25, "convencao": 0.03, "radiacao": 0.7},
    "Isopor": {"conducao": 0.03, "convencao": 0.01, "radiacao": 0.1},
    "Madeira": {"conducao": 0.15, "convencao": 0.03, "radiacao": 0.5},
}

LAMPADAS = {
    "Vapor de Mercúrio": 150,
    "Fluorescente": 100,
    "LED": 50,
    "Incandescente": 200,
    "Neon": 120,
}

def calcular_fluxo_termico(k, h, emissividade, area, delta_temp, espessura):
    # Condução
    q_conducao = k * area * delta_temp / espessura
    # Convecção
    q_convencao = h * area * delta_temp
    # Radiação
    q_radiacao = emissividade * area * delta_temp ** 4  # Simplificação para cálculo
    return q_conducao + q_convencao + q_radiacao

def calcular_btu(inputs):
    area_total = sum([float(p['area']) for p in inputs['paredes']])
    delta_temp = abs(inputs['temperatura_externa'] - inputs['temperatura_interna'])

    q_total = 0
    for parede in inputs['paredes']:
        material = MATERIAIS[parede['material']]
        q_parede = calcular_fluxo_termico(
            k=material['conducao'],
            h=material['convencao'],
            emissividade=material['radiacao'],
            area=float(parede['area']),
            delta_temp=delta_temp,
            espessura=float(parede['espessura']),
        )
        q_total += q_parede

    # Adicionar calor das lâmpadas
    q_lampadas = sum(LAMPADAS[lam['tipo']] * int(lam['quantidade']) for lam in inputs['lampadas'])

    # Calor humano (600 BTU por pessoa)
    q_pessoas = int(inputs['pessoas']) * 600

    # Total em BTU com margem de segurança de 10%
    btu_total = (q_total + q_lampadas + q_pessoas) * 1.1
    return round(btu_total, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Coleta os dados do formulário
        paredes = [
            {
                "material": request.form.get(f"material_{i}"),
                "area": request.form.get(f"area_{i}"),
                "espessura": request.form.get(f"espessura_{i}")
            }
            for i in range(6)
        ]
        lampadas = [
            {
                "tipo": request.form.get(f"lampada_tipo_{i}"),
                "quantidade": request.form.get(f"lampada_quantidade_{i}")
            }
            for i in range(2)
        ]
        pessoas = request.form.get("pessoas")
        temperatura_interna = float(request.form.get("temperatura_interna"))
        temperatura_externa = float(request.form.get("temperatura_externa"))
        
        inputs = {
            "paredes": paredes,
            "lampadas": lampadas,
            "pessoas": pessoas,
            "temperatura_interna": temperatura_interna,
            "temperatura_externa": temperatura_externa,
        }
        
        resultado_btu = calcular_btu(inputs)
        return render_template("index.html", resultado_btu=resultado_btu, materiais=MATERIAIS, lampadas=LAMPADAS)
    
    return render_template("index.html", materiais=MATERIAIS, lampadas=LAMPADAS)

if __name__ == "__main__":
    app.run(debug=True)