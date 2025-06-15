import streamlit as st
from database import (
    init_db,
    registrar_cortes,
    obtener_registros,
    obtener_resumen,
    obtener_cortes_por_mes,
    eliminar_corte,
    actualizar_corte,
    registrar_venta,
    obtener_ventas,
    obtener_resumen_mensual,
    registrar_producto,
    obtener_productos,
    eliminar_producto,
    actualizar_producto,
    registrar_gasto,
    obtener_gastos_por_mes
)
from datetime import date
import calendar

# Inicializar la base de datos
init_db()

# Estilo visual
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #002244 !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    .stButton > button {
        background-color: #8B0000;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
        border: none;
    }
    .stButton > button:hover {
        background-color: #B22222;
    }
    html, body, .stApp {
        background-color: white;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Menú lateral
st.sidebar.title("📋 Menú")
opcion = st.sidebar.radio("Ir a:", ["Registro de cortes", "Gestión mensual y ventas", "Inventario"])

# Título principal
st.markdown("## 💈 Sistema de Gestión para Barbería")
if opcion == "Registro de cortes":
    st.subheader("✂️ Registro diario de cortes")

    with st.form("registro_cortes"):
        fecha = st.date_input("Fecha", value=date.today())
        cantidad = st.number_input("Cantidad de cortes", min_value=0, step=1)
        ganancias = st.number_input("Ganancia total del día (₡)", min_value=0.0, step=100.0, format="%.2f")
        registrar = st.form_submit_button("Guardar")

        if registrar:
            fecha_str = fecha.strftime("%Y-%m-%d")
            exito = registrar_cortes(fecha_str, cantidad, ganancias)
            if exito:
                st.success("✅ Corte registrado correctamente")
                st.rerun()
            else:
                st.error("⚠️ Ya existe un registro para esta fecha.")

    st.subheader("📅 Historial de cortes registrados")
    registros = obtener_registros()
    if registros:
        for i, registro in enumerate(registros):
            if len(registro) != 3:
                continue
            fecha, cantidad, ganancia = registro
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            col1.markdown(f"📌 **{fecha}** — Cortes: {cantidad}, Ganancia: ₡{ganancia:,.2f}")
            with col3:
                if st.button("✏️", key=f"edit_corte_{i}"):
                    with st.form(f"form_edit_corte_{i}"):
                        nueva_cantidad = st.number_input("Nueva cantidad de cortes", min_value=0, value=cantidad, key=f"cant_{i}")
                        nueva_ganancia = st.number_input("Nueva ganancia", min_value=0.0, value=ganancia, format="%.2f", key=f"gan_{i}")
                        actualizar = st.form_submit_button("Actualizar")
                        if actualizar:
                            actualizar_corte(fecha, nueva_cantidad, nueva_ganancia)
                            st.success("✅ Registro actualizado")
                            st.rerun()
            with col4:
                if st.button("🗑️", key=f"del_corte_{i}"):
                    eliminar_corte(fecha)
                    st.success("✅ Registro eliminado")
                    st.rerun()
    else:
        st.info("No hay cortes registrados todavía.")

    st.subheader("📊 Resumen general")
    resumen = obtener_resumen()
    total_cortes = resumen[0] or 0
    total_ganancias = resumen[1] or 0.0
    st.success(f"💇‍♂️ Total de cortes: **{total_cortes}** — 💰 Ganancia acumulada: **₡{total_ganancias:,.2f}**")
elif opcion == "Gestión mensual y ventas":
    st.subheader("📅 Gestión mensual de cortes, ventas y gastos")

    col1, col2 = st.columns(2)
    with col1:
        anio = st.selectbox("Seleccione el año", options=list(range(2022, date.today().year + 1)), index=1)
    with col2:
        meses_es = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
]

mes = st.selectbox("Seleccione el mes", options=meses_es, format_func=lambda x: x[1])[0]


    cortes = obtener_cortes_por_mes(anio, mes)
    ventas = obtener_ventas()
    gastos = obtener_gastos_por_mes(anio, mes)
    resumen = obtener_resumen_mensual(anio, mes)

    st.markdown("### ✂️ Cortes realizados")
    if cortes:
        for c in cortes:
            st.write(f"📌 {c[0]} — Cortes: {c[1]} — Ganancia: ₡{c[2]:,.2f}")
    else:
        st.info("No hay cortes registrados para este mes.")

    st.markdown("### 🧴 Ventas registradas")
    ventas_mes = [v for v in ventas if v[0][:7] == f"{anio}-{mes:02d}"]
    if ventas_mes:
        for v in ventas_mes:
            st.write(f"🗓️ {v[0]} — Producto: {v[1]} — Cantidad: {v[2]} — Total: ₡{v[3]:,.2f}")
    else:
        st.info("No hay ventas registradas.")

    st.markdown("### 💸 Gastos del mes")
    if gastos:
        for g in gastos:
            st.write(f"🗓️ {g[0]} — {g[1]} — ₡{g[2]:,.2f}")
    else:
        st.info("No hay gastos registrados.")

    st.markdown("### 📊 Resumen del mes")
    st.success(f"✂️ Cortes: {resumen['cortes_realizados']} — 💰 Ganancia cortes: ₡{resumen['ganancia_cortes']:,.2f}")
    st.success(f"🧴 Productos vendidos: {resumen['productos_vendidos']} — Ganancia ventas: ₡{resumen['ganancia_ventas']:,.2f}")
    st.warning(f"💸 Gastos totales: ₡{resumen['total_gastos']:,.2f}")

    st.markdown("## ➕ Registrar nueva venta")
    with st.form("form_venta"):
        fecha_venta = st.date_input("Fecha", value=date.today())
        producto = st.text_input("Producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        total = st.number_input("Total ₡", min_value=0.0, step=100.0, format="%.2f")
        registrar = st.form_submit_button("Guardar venta")
        if registrar:
            registrar_venta(fecha_venta.strftime("%Y-%m-%d"), producto, cantidad, total)
            st.success("✅ Venta registrada")
            st.rerun()

    st.markdown("## ➕ Registrar nuevo gasto")
    with st.form("form_gasto"):
        fecha_gasto = st.date_input("Fecha gasto", value=date.today())
        descripcion = st.text_input("Descripción")
        monto = st.number_input("Monto ₡", min_value=0.0, step=100.0, format="%.2f")
        guardar_gasto = st.form_submit_button("Guardar gasto")
        if guardar_gasto:
            registrar_gasto(fecha_gasto.strftime("%Y-%m-%d"), descripcion, monto)
            st.success("✅ Gasto registrado")
            st.rerun()
elif opcion == "Inventario":
    st.subheader("📦 Inventario de productos")

    st.markdown("### ➕ Registrar nuevo producto")
    with st.form("form_nuevo_producto"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad en stock", min_value=0, step=1)
        costo = st.number_input("Costo por unidad (₡)", min_value=0.0, step=100.0, format="%.2f")
        guardar_producto = st.form_submit_button("Guardar producto")
        if guardar_producto:
            registrar_producto(nombre, cantidad, costo)
            st.success("✅ Producto registrado correctamente")
            st.rerun()

    st.markdown("### 📋 Lista de productos registrados")
    productos = obtener_productos()
    if productos:
        for i, (nombre, cantidad, costo) in enumerate(productos):
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            alerta = " 🔴" if cantidad < 3 else ""
            col1.markdown(f"🧴 **{nombre}**{alerta}")
            col2.markdown(f"Stock: {cantidad}")
            col3.markdown(f"₡{costo:,.2f}")

            with col4:
                if st.button("✏️", key=f"edit_prod_{i}"):
                    with st.form(f"form_edit_producto_{i}"):
                        nueva_cantidad = st.number_input("Nueva cantidad", value=cantidad, min_value=0, key=f"cant_{i}")
                        nuevo_costo = st.number_input("Nuevo costo", value=costo, min_value=0.0, key=f"costo_{i}", format="%.2f")
                        actualizar = st.form_submit_button("Actualizar")
                        if actualizar:
                            actualizar_producto(nombre, nueva_cantidad, nuevo_costo)
                            st.success("✅ Producto actualizado")
                            st.rerun()

                if st.button("🗑️", key=f"del_prod_{i}"):
                    eliminar_producto(nombre)
                    st.success("✅ Producto eliminado")
                    st.rerun()
    else:
        st.info("No hay productos registrados.")



