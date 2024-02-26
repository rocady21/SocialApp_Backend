from flask import Blueprint,jsonify,request
from models import db,Estado,CuestionarioUser,Entidad,Insignia,Opciones,Respuesta,Categoria,Preguntas,Cuestionario,User
from datetime import datetime,timedelta


def generate_bp_questions():
    from app import app
    questions_bp = Blueprint("questions",__name__)

    @questions_bp.route("/mensaje",methods = ["GET"])
    def Mostrar_mensaje():
        return jsonify({"ok":True,"msg":"Correctoooooooo"})

    @questions_bp.route("/api/category", methods=["POST"])
    def crear_categoria():
        response = request.json

        new_cateogry = Entidad(
            nombre=response["nombre"],
            foto= response["foto"],
            id_categoria= response["id_categoria"]
        )

        db.session.add(new_cateogry)
        db.session.commit()
        return jsonify({"ok":True,"msg":" Entidad creada exitosamente"}),200


    # ruta para crear questionario
    # se necesitara el nombre, las preguntas y las opciones
    @questions_bp.route("/api/questions",methods = ["POST"])
    def Create_question():
        response = request.json


        now = datetime.now()

        fecha_sumada = now + timedelta(days=response["fin_in_days"])

        fecha_sumada_str = fecha_sumada.strftime("%Y-%m-%d %H:%M:%S")
        # validamos que exista la insignia y la entidad

        insignia_exist = Insignia.query.filter_by(id=response["id_insignia"]).first()
        entidad_exist = Entidad.query.filter_by(id=response["id_entidad"]).first()

        if insignia_exist is None or entidad_exist is None:
            return jsonify({"ok":False,"msg":"debe de ingresar una insignia o entidad existente"})

        nuevo_cuestionario = Cuestionario(
            nombre="One piece",
            descripcion="Cuestionario de one piece",
            max_p=100,
            entidad_id = response["id_entidad"],
            id_insignia=response["id_insignia"],
            inicio=now,
            fin=fecha_sumada_str,
        )

        print("JASJDNNNNNNNNNNNNNNNNNNNNNNN")

        db.session.add(nuevo_cuestionario)
        db.session.commit()

        nuevo_cuestionario_f = nuevo_cuestionario.serialize()
        # ahora crearemos las preguntas

        if len(response["preguntas"]) != 0:

            preguntas = response["preguntas"]

            def create_questions_and_options(item):

                preg = item["pregunta"]
                print(nuevo_cuestionario_f["id"])
                new_pregunta = Preguntas(
                    texto=preg,
                    id_cuestionario	= nuevo_cuestionario_f["id"],
                    puntos = item["points"],
                    foto = item["foto"] if "foto" in item else None

                )

                db.session.add(new_pregunta)
                db.session.commit()
                pregunta_f = new_pregunta.serialize()
                # ahora creamos las opciones

                options = item["opciones"]

                try:
                    for y in options:
                        #creamos cada una de las opciones
                        print(y)
                        

                        new_option = Opciones(
                            id_pregunta=pregunta_f["id"],
                            texto=y["text"],
                            is_true=y["is_true"]              

                        )

                        db.session.add(new_option)
                        db.session.commit()
                except Exception as e:
                    print(e)

            for x in preguntas:
                create_questions_and_options(x)

            return jsonify({"ok":True,"msg":"Cuestionario creado exitosamente"}),200

        else:
            return jsonify({"ok":False,"msg":"Debe de ingresar opciones"}),400
        

    @questions_bp.route("/api/questions/<int:id_questions>",methods =["DELETE"])
    def delete_questions(id_questions):
        
        cuestionario = Cuestionario.query.filter_by(id=id_questions).first()
        cuest_f = cuestionario.serialize()
        # buscamos las preguntas
        preguntas = Preguntas.query.filter(Preguntas.id_cuestionario == cuest_f["id"]).all()

        if len(preguntas) != 0:
            for x in preguntas:
                xF = x.serialize()
                # buscamos las opciones
                options = Opciones.query.filter(Opciones.id_pregunta == xF["id"]).all()

                if len(options) != 0:
                    for y in options:
                        db.session.delete(y)
                        db.session.commit()
                db.session.delete(x)
                db.session.commit()


        db.session.delete(cuestionario)
        db.session.commit()
        
        return jsonify({"ok":True,"msg":"Cuestionario borrado exitosamente"})
    
    # cargar entidades de una categoria


    @questions_bp.route("/api/category/<int:id_category>",methods =["GET"])
    def load_entitys_from_categories(id_category):
        
        load_entities = Entidad.query.filter(Entidad.id_categoria == id_category).all()


        if len(load_entities) != 0:
            def laod_data(it):
                item = it.serialize()

                return {
                    "id": item["id"],
                    "nombre":item["nombre"],
                    "foto":item["foto"]
                }

            result = list(map(lambda item:laod_data(item),load_entities))

            
            return jsonify({"ok":True,"data":result}),200
        else:
            return jsonify({"ok":False,"msg":"Esta categoria no tiene entidades"}),200
    
    #cargar cuestionarios de una entidad

    #cargar info de cuestionario
    @questions_bp.route("/api/questions/<int:id_question>",methods =["GET"])
    def load_info_questions_by_entity(id_question):
        
        #traemos el cuestionario

        cuestionario = Cuestionario.query.filter_by(id=id_question).first()
        if cuestionario:
            cuest_f = cuestionario.serialize()
            info_insignia = Insignia.query.filter_by(id=cuest_f["id_insignia"]).first()
            insignia_f = info_insignia.serialize()
            questions = Preguntas.query.filter(Preguntas.id_cuestionario == cuest_f["id"] ).all()

            def load_info_questions(it):
                item = it.serialize()
                # cargaremos las opciones de cada pregunta
                options = Opciones.query.filter(Opciones.id_pregunta == item["id"]).all()
                
                def load_info_options(it):
                    item = it.serialize()
                    return {
                        "id":item["id"],
                        "texto":item["texto"]
                    }
                
                load_info_opt = list(map(lambda item:load_info_options(item),options))

                return {
                    "id":item["id"],
                    "texto": item["texto"],
                    "puntos":item["puntos"],
                    "foto":item["foto"],
                    "opciones":load_info_opt
                }


            result_questions = list(map(lambda item:load_info_questions(item),questions))

            return jsonify({"ok":True,"msg":"","data":{
                "nombre":cuest_f["nombre"],
                "descripcion":cuest_f["descripcion"],
                "inicio":cuest_f["inicio"],
                "fin":cuest_f["fin"],
                "insignia":insignia_f,
                "number_of_questions":len(questions),
                "questions":result_questions
            }}),200

        else: 
            return jsonify({"ok":False,"msg":"No hay cuest con ese id"}),400
    



    # creacion de la tabla de respuesta del usaurio 
    @questions_bp.route("/api/questions/user",methods=["POST"])
    def create_user_response_table():
        response = request.json

        cuest_exist = Cuestionario.query.filter_by(id=response["id_cuestionario"]).first()
        user_exist = User.query.filter_by(id=response["user"]).first()

        if user_exist is not None and cuest_exist is not None:
            new_cuest_user = CuestionarioUser(
                id_cuestionario=response["id_cuestionario"],
                id_user=response["id_user"],
                id_estado=1
            )
            db.session.add(new_cuest_user),
            db.session.commit()
            return jsonify({"ok":True, "msg":"Cuestionario creado exitosamente"}),200
        return jsonify({"ok":False,"msg":"debe exisir el user y el cuestionario "}),400




    # insertamos las resp del usuario una por una
    @questions_bp.route("/api/questions/user/response",methods=["POST"])
    def create_user_response():
        response = request.json
        id_cueest = response["id_cuest"]
        for x in response["response"]:
            new_resp = Respuesta(
                id_cuestionario_user=x["id_cuestionario_user"],
                id_opcion=x["id_opcion"]
            )
            db.session.add(new_resp)
            db.session.commit()

        #buscamos el cuestionario del user y lo finalizamos
        cuest_exist = Cuestionario.query.filter_by(id=id_cueest).first()
        cuest_exist.id_estado = 2
        db.session.add(cuest_exist),
        db.session.commit()
        return jsonify({"ok":True, "msg":"Respuestas insertadas correctamente"})
    

    @questions_bp.route("/api/valid_response",methods=["POST"])
    def valid_responses():

        return jsonify({"ok":True, "msg":"Respuestas insertadas correctamente"})


    return questions_bp