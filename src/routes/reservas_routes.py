import random

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")

@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas

@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        existe_reserva_com_mesmo_documento = session.exec(
            select(Reserva).where(
                Reserva.documento == reserva.documento,
            )
        ).all()

        if len(existe_reserva_com_mesmo_documento) > 0:
            return JSONResponse(
                content={"message": "Você não pode reservar um voo com o mesmo documento."},
                status_code=404,
            )

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        reserva = session.exec(statement).first()

        if reserva is None:
            raise HTTPException(
                status_code=404,
                detail=f"Reserva com o código {codigo_reserva} não encontrada."
            )

        statement = select(Voo).where(Voo.id == reserva.voo_id)
        voo = session.exec(statement).first()

        poltrona_atual = getattr(voo, f"poltrona_{num_poltrona}")

        if poltrona_atual is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Poltrona {num_poltrona} já ocupada."
            )

        setattr(voo, f"poltrona_{num_poltrona}", codigo_reserva)

        session.add(voo)
        session.commit()
        session.refresh(voo)

        return {"message": f"Check-in realizado com sucesso para a reserva {codigo_reserva} na poltrona {num_poltrona}."}

@reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin_patch(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)
        reserva = session.exec(statement).first()

        if not reserva:
            raise HTTPException(
                status_code=404,
                detail=f"Reserva com o código {codigo_reserva} não encontrada."
            )

        statement = select(Voo).where(Voo.id == reserva.voo_id)
        voo = session.exec(statement).first()

        poltrona_atual = getattr(voo, f"poltrona_{num_poltrona}")

        if poltrona_atual is not None:
            raise HTTPException(
                status_code=403,
                detail=f"Poltrona {num_poltrona} já ocupada."
            )

        setattr(voo, f"poltrona_{num_poltrona}", codigo_reserva)

        session.add(voo)
        session.commit()
        session.refresh(voo)

        return {"message": f"Check-in realizado com sucesso para a reserva {codigo_reserva} na poltrona {num_poltrona}."}
