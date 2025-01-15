from odoo import models, fields

class LigaPartidoWizard(models.TransientModel):
    _name = 'liga.partido.wizard'
    _description = 'Wizard para crear un partido'

    equipo_casa = fields.Many2one('liga.equipo', string="Equipo Local", required=True)
    equipo_fuera = fields.Many2one('liga.equipo', string="Equipo Visitante", required=True)
    goles_casa = fields.Integer(string="Goles Local", default=0)
    goles_fuera = fields.Integer(string="Goles Visitante", default=0)

    def add_liga_partido(self):
        partido_model = self.env['liga.partido']
        for wiz in self:
            partido_model.create({
                'equipo_casa': wiz.equipo_casa.id,
                'equipo_fuera': wiz.equipo_fuera.id,
                'goles_casa': wiz.goles_casa,
                'goles_fuera': wiz.goles_fuera,
            })
