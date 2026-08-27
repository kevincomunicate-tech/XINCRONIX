<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Http\Controllers\Controller;
use App\Models\Usuario;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class UsuarioController extends Controller
{
    use RespondsWithJson;

    public function index(Request $request)
    {
        $query = Usuario::with(['empresa', 'rol', 'perfil']);

        if ((int) $request->user()->id_roles !== 1) {
            $query->where('id_empresa', $request->user()->id_empresa);
        }

        return $this->success($query->orderBy('nombres')->orderBy('apellidos')->get(), 'Usuarios obtenidos');
    }

    public function store(Request $request)
    {
        if ((int) $request->user()->id_roles !== 1) {
            return $this->error('No tienes permiso para crear usuarios', 403);
        }

        $validator = Validator::make($request->all(), [
            'nombres' => ['required', 'string', 'max:100'],
            'apellidos' => ['nullable', 'string', 'max:100'],
            'email' => ['required', 'email', 'max:150', Rule::unique('usuarios', 'email')],
            'password' => ['required', 'string', 'min:8', 'max:128'],
            'cargo' => ['nullable', 'string', 'max:80'],
            'telefono' => ['nullable', 'string', 'max:20'],
            'avatar' => ['nullable', 'string', 'max:255'],
            'estado' => ['nullable', 'boolean'],
            'id_empresa' => ['nullable', 'integer', Rule::exists('empresa', 'id_empresa')],
            'id_roles' => ['nullable', 'integer', Rule::exists('roles', 'id_roles')],
            'id_perfil' => ['nullable', 'integer', Rule::exists('perfiles_especificos', 'id_perfil')],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $data = $validator->validated();
        $data['id_empresa'] = (int) ($data['id_empresa'] ?? $request->user()->id_empresa);
        $data['password'] = Hash::make($data['password']);
        $data['fecha_creacion'] = now();

        $usuario = Usuario::create($data);

        return $this->success($usuario->load(['empresa', 'rol', 'perfil']), 'Usuario creado', 201);
    }

    public function show(Request $request, string $id)
    {
        $usuario = Usuario::with(['empresa', 'rol', 'perfil'])->find($id);

        if (! $usuario) {
            return $this->error('Usuario no encontrado', 404);
        }

        if ((int) $request->user()->id_roles !== 1 && (int) $request->user()->id_empresa !== (int) $usuario->id_empresa) {
            return $this->error('No tienes permiso para ver este usuario', 403);
        }

        return $this->success($usuario);
    }

    public function update(Request $request, string $id)
    {
        $usuario = Usuario::find($id);

        if (! $usuario) {
            return $this->error('Usuario no encontrado', 404);
        }

        if ((int) $request->user()->id_roles !== 1 && (int) $request->user()->id_empresa !== (int) $usuario->id_empresa) {
            return $this->error('No tienes permiso para editar este usuario', 403);
        }

        $validator = Validator::make($request->all(), [
            'nombres' => ['sometimes', 'string', 'max:100'],
            'apellidos' => ['sometimes', 'nullable', 'string', 'max:100'],
            'email' => ['sometimes', 'email', 'max:150', Rule::unique('usuarios', 'email')->ignore($usuario->id_usuario, 'id_usuario')],
            'password' => ['sometimes', 'nullable', 'string', 'min:8', 'max:128'],
            'cargo' => ['sometimes', 'nullable', 'string', 'max:80'],
            'telefono' => ['sometimes', 'nullable', 'string', 'max:20'],
            'avatar' => ['sometimes', 'nullable', 'string', 'max:255'],
            'estado' => ['sometimes', 'boolean'],
            'id_empresa' => ['sometimes', 'nullable', 'integer', Rule::exists('empresa', 'id_empresa')],
            'id_roles' => ['sometimes', 'nullable', 'integer', Rule::exists('roles', 'id_roles')],
            'id_perfil' => ['sometimes', 'nullable', 'integer', Rule::exists('perfiles_especificos', 'id_perfil')],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $data = $validator->validated();

        if (array_key_exists('password', $data) && filled($data['password'])) {
            $data['password'] = Hash::make($data['password']);
        }

        if (! array_key_exists('id_empresa', $data) && (int) $request->user()->id_roles !== 1) {
            $data['id_empresa'] = $request->user()->id_empresa;
        }

        $usuario->update($data);

        return $this->success($usuario->fresh()->load(['empresa', 'rol', 'perfil']), 'Usuario actualizado');
    }

    public function destroy(Request $request, string $id)
    {
        if ((int) $request->user()->id_roles !== 1) {
            return $this->error('Solo un administrador puede eliminar usuarios', 403);
        }

        if ((int) $request->user()->id_usuario === (int) $id) {
            return $this->error('No puedes eliminar tu propio usuario', 403);
        }

        $deleted = Usuario::where('id_usuario', $id)->delete();

        if (! $deleted) {
            return $this->error('Usuario no encontrado', 404);
        }

        return $this->success(null, 'Usuario eliminado');
    }
}