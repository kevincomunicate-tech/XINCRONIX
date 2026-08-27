<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Models\Equipo;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class EquipoController extends Controller
{
    use RespondsWithJson;

    public function index(Request $request)
    {
        $equipos = Equipo::where('id_empresa', $request->user()->id_empresa)
            ->orderBy('nombre')
            ->get();

        return $this->success($equipos, 'Equipos obtenidos');
    }

    public function store(Request $request)
    {
        if (! in_array((int) $request->user()->id_roles, [1, 2], true)) {
            return $this->error('No tienes permiso para crear equipos', 403);
        }

        $validator = Validator::make($request->all(), [
            'nombre' => ['required', 'string', 'max:150'],
            'descripcion' => ['nullable', 'string'],
            'miembros' => ['nullable', 'integer', 'min:0'],
            'fecha_inicio' => ['nullable', 'date'],
            'fecha_fin' => ['nullable', 'date', 'after_or_equal:fecha_inicio'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $equipo = Equipo::create($validator->safe()->merge(['id_empresa' => $request->user()->id_empresa])->all());

        return $this->success($equipo, 'Equipo creado', 201);
    }

    public function show(Request $request, string $id)
    {
        $equipo = Equipo::where('id_empresa', $request->user()->id_empresa)->find($id);

        if (! $equipo) {
            return $this->error('Equipo no encontrado', 404);
        }

        return $this->success($equipo);
    }

    public function update(Request $request, string $id)
    {
        if (! in_array((int) $request->user()->id_roles, [1, 2], true)) {
            return $this->error('No tienes permiso para editar equipos', 403);
        }

        $equipo = Equipo::where('id_empresa', $request->user()->id_empresa)->find($id);

        if (! $equipo) {
            return $this->error('Equipo no encontrado', 404);
        }

        $validator = Validator::make($request->all(), [
            'nombre' => ['sometimes', 'string', 'max:150'],
            'descripcion' => ['nullable', 'string'],
            'miembros' => ['nullable', 'integer', 'min:0'],
            'fecha_inicio' => ['nullable', 'date'],
            'fecha_fin' => ['nullable', 'date', 'after_or_equal:fecha_inicio'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $equipo->update($validator->validated());

        return $this->success($equipo, 'Equipo actualizado');
    }

    public function destroy(Request $request, string $id)
    {
        if (! in_array((int) $request->user()->id_roles, [1, 2], true)) {
            return $this->error('No tienes permiso para eliminar equipos', 403);
        }

        $deleted = Equipo::where('id_empresa', $request->user()->id_empresa)->whereKey($id)->delete();

        if (! $deleted) {
            return $this->error('Equipo no encontrado', 404);
        }

        return $this->success(null, 'Equipo eliminado');
    }
}
