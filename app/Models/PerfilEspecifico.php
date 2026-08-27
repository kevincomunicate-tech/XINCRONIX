<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class PerfilEspecifico extends Model
{
    protected $table = 'perfiles_especificos';
    protected $primaryKey = 'id_perfil';
    public $timestamps = false;

    protected $guarded = [];

    public function usuarios(): HasMany
    {
        return $this->hasMany(Usuario::class, 'id_perfil');
    }
}