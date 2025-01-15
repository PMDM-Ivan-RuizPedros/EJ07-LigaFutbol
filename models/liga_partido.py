# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LigaPartido(models.Model):
    #Nombre y descripcion del modelo
    _name = 'liga.partido'
    _description = 'Un partido de la liga'


    #Atributos del modelo


    #PARA CUANDO NO HAY UN ATRIBUTO LLAMADO NAME PARA MOSTRAR LOS Many2One en Vistas
    # https://www.odoo.com/es_ES/forum/ayuda-1/how-defined-display-name-in-custom-many2one-91657
    
   

    #Nombre del equipo que juega en casa casa
    equipo_casa = fields.Many2one(
        'liga.equipo',
        string='Equipo local',
    )
    #Goles equipo de casa
    goles_casa= fields.Integer()

    #Nombre del equipo que juega fuera
    equipo_fuera = fields.Many2one(
        'liga.equipo',
        string='Equipo visitante',
    )
    #Goles equipo de casa
    goles_fuera= fields.Integer()
    
    #Constraints de atributos
    @api.constrains('equipo_casa')
    def _check_mismo_equipo_casa(self):
        for record in self:
            if not record.equipo_casa:
                raise models.ValidationError('Debe seleccionarse un equipo local.')
            if record.equipo_casa == record.equipo_fuera:
                raise models.ValidationError('Los equipos del partido deben ser diferentes.')


     #Constraints de atributos
    @api.constrains('equipo_fuera')
    def _check_mismo_equipo_fuera(self):
        for record in self:
            if not record.equipo_fuera:
                raise models.ValidationError('Debe seleccionarse un equipo visitante.')
            if record.equipo_fuera and record.equipo_casa == record.equipo_fuera:
                raise models.ValidationError('Los equipos del partido deben ser diferentes.')




    
    '''
    Funcion para actualizar la clasificacion de los equipos, re-calculandola entera
    '''
    def calcularPuntosDiferencia(self, goles_casa, goles_fuera):
        if abs(goles_casa - goles_fuera) >= 4:
            if goles_casa > goles_fuera:
                return (4, -1)
            elif goles_fuera > goles_casa:
                return (-1, 4)
        if goles_casa > goles_fuera:
            return (3, 0)
        elif goles_fuera > goles_casa:
            return (0, 3)
        return (1, 1)

    def actualizoRegistrosEquipo(self):
        #Recorremos partidos y equipos
        for recordEquipo in self.env['liga.equipo'].search([]):
            #Como recalculamos todo, ponemos de cada equipo todo a cero
            recordEquipo.victorias=0
            recordEquipo.empates=0
            recordEquipo.derrotas=0
            recordEquipo.goles_a_favor=0
            recordEquipo.goles_en_contra=0
            
            for recordPartido in self.env['liga.partido'].search([]):  
                puntos_casa, puntos_fuera = self.calcularPuntosDiferencia(recordPartido.goles_casa, recordPartido.goles_fuera)

                #Si es el equipo de casa
                if recordPartido.equipo_casa.nombre==recordEquipo.nombre:
                    recordEquipo.victorias += puntos_casa == 4 or puntos_casa == 3
                    recordEquipo.derrotas += puntos_fuera == 4 or puntos_fuera == 3
                    recordEquipo.empates += puntos_casa == 1
                    recordEquipo.goles_a_favor += recordPartido.goles_casa
                    recordEquipo.goles_en_contra += recordPartido.goles_fuera

                #Si es el equipo de fuera
                if recordPartido.equipo_fuera.nombre==recordEquipo.nombre:
                    recordEquipo.victorias += puntos_fuera == 4 or puntos_fuera == 3
                    recordEquipo.derrotas += puntos_casa == 4 or puntos_casa == 3
                    recordEquipo.empates += puntos_fuera == 1
                    recordEquipo.goles_a_favor += recordPartido.goles_fuera
                    recordEquipo.goles_en_contra += recordPartido.goles_casa



    #API onchange para cuando se modifica un partido
    #Aunque onchange envia un registro, hacemos codigo para recalcular 
    #http://www.geninit.cn/developer/reference/orm.html  
    @api.onchange('equipo_casa', 'goles_casa', 'equipo_fuera', 'goles_fuera')
    def actualizar(self):
        self.actualizoRegistrosEquipo()
    
    def añadir_goles_locales(self):
        for partido in self.search([]):
            partido.goles_casa += 2
        self.actualizoRegistrosEquipo()

    def añadir_goles_visitantes(self):
        for partido in self.search([]):
            partido.goles_fuera += 2
        self.actualizoRegistrosEquipo()

    #Sobrescribo el borrado (unlink)
    def unlink(self):
        #Borro el registro, que es lo que hace el metodo normalmente
        result=super(LigaPartido,self).unlink()
        #Añado que llame a actualizoRegistroEquipo()
        self.actualizoRegistrosEquipo()
        return result

    #Sobreescribo el metodo crear
    @api.model
    def create(self, values):
        #hago lo normal del metodo create
        result = super().create(values)
        #Añado esto: llamo a la funcion que actualiza la clasificacion
        self.actualizoRegistrosEquipo()
        #hago lo normal del metodo create
        return result
