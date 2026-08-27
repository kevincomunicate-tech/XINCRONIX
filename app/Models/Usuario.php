<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class Usuario extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $table = 'usuarios';
    protected $primaryKey = 'id_usuario';
    public $timestamps = false;

    protected $guarded = [];

    protected $hidden = ['password'];

    protected $casts = [
        'estado' => 'boolean',
        'password' => 'hashed',
        'fecha_creacion' => 'datetime',
    ];

    public function empresa(): BelongsTo
    {
        return $this->belongsTo(Empresa::class, 'id_empresa');
    }

    public function rol(): BelongsTo
    {
        return $this->belongsTo(Rol::class, 'id_roles');
    }

    public function perfil(): BelongsTo
    {
        return $this->belongsTo(PerfilEspecifico::class, 'id_perfil');
    }

    public function tareas(): HasMany
    {
        return $this->hasMany(Tarea::class, 'id_usuario');
    }

    public function mensajesEnviados(): HasMany
    {
        return $this->hasMany(Mensaje::class, 'id_usuario');
    }

    public function mensajesRecibidos(): HasMany
    {
        return $this->hasMany(Mensaje::class, 'id_destinatario');
    }

    public function notificaciones(): HasMany
    {
        return $this->hasMany(Notificacion::class, 'id_usuario');
    }

    public function reuniones(): HasMany
    {
        return $this->hasMany(Reunion::class, 'id_usuario');
    }

    public function calendario(): HasMany
    {
        return $this->hasMany(Calendario::class, 'id_usuario');
    }

    public function metricas(): HasMany
    {
        return $this->hasMany(MetricaRendimiento::class, 'id_usuario');
    }
}
