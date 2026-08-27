<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Empresa extends Model
{
    protected $table = 'empresa';
    protected $primaryKey = 'id_empresa';
    public $timestamps = false;

    protected $guarded = [];

    protected $casts = [
        'fecha_actualizacion' => 'datetime',
        'fecha_creacion' => 'datetime',
    ];

    public function usuarios(): HasMany
    {
        return $this->hasMany(Usuario::class, 'id_empresa');
    }

    public function proyectos(): HasMany
    {
        return $this->hasMany(Proyecto::class, 'id_empresa');
    }

    public function equipos(): HasMany
    {
        return $this->hasMany(Equipo::class, 'id_empresa');
    }

    public function solicitudesPago(): HasMany
    {
        return $this->hasMany(SolicitudPago::class, 'id_empresa');
    }

    public function ticketsSoporte(): HasMany
    {
        return $this->hasMany(TicketSoporte::class, 'id_empresa');
    }
}
