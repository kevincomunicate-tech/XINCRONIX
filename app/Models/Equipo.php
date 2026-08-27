<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Equipo extends Model
{
    protected $table = 'equipos';
    protected $primaryKey = 'id_equipo';
    public $timestamps = false;

    protected $guarded = [];

    protected $casts = [
        'fecha_inicio' => 'datetime',
        'fecha_fin' => 'datetime',
    ];

    public function empresa(): BelongsTo
    {
        return $this->belongsTo(Empresa::class, 'id_empresa');
    }

    public function proyectos(): HasMany
    {
        return $this->hasMany(Proyecto::class, 'id_equipo');
    }

    public function tareas(): HasMany
    {
        return $this->hasMany(Tarea::class, 'id_equipo');
    }

    public function reuniones(): HasMany
    {
        return $this->hasMany(Reunion::class, 'id_equipo');
    }
}