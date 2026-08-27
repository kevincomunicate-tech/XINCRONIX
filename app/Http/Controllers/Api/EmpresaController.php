<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Models\Empresa;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;

class EmpresaController extends Controller
{
    use RespondsWithJson;

    public function index(Request $request)
    {
        $query = Empresa::withCount(['usuarios', 'proyectos', 'equipos']);

        if ((int) $request->user()->id_roles !== 1) {
            $query->where('id_empresa', $request->user()->id_empresa);
        }

        $empresas = $query->orderBy('nombre')->get();

        if ($request->expectsJson() || $request->is('api/*')) {
            return $this->success($empresas, 'Empresas obtenidas');
        }

        return view('admin_panel', ['empresasIniciales' => $empresas]);
    }

    public function store(Request $request)
    {
        if ((int) $request->user()->id_roles !== 1) {
            return $this->error('No tienes permiso para crear empresas', 403);
        }

        $validator = Validator::make($request->all(), [
            'nombre' => ['required', 'string', 'max:200'],
            'nit' => ['required', 'string', 'max:30', Rule::unique('empresa', 'nit')],
            'email' => ['required', 'email', 'max:150', Rule::unique('empresa', 'email')],
            'telefono' => ['nullable', 'string', 'max:20'],
            'direccion' => ['nullable', 'string', 'max:300'],
            'industria' => ['nullable', 'string', 'max:100'],
            'plan_suscripcion' => ['nullable', 'string', 'max:50'],
            'sector' => ['nullable', 'string', 'max:50'],
            'administrador' => ['nullable', 'string', 'max:120'],
            'num_empleados' => ['nullable', 'string', 'max:30'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $empresa = Empresa::create($validator->safe()->merge(['fecha_creacion' => now()])->all());

        return $this->success($empresa, 'Empresa creada', 201);
    }
    public function show(Request $request, string $id)
    {
        if ((int) $request->user()->id_roles !== 1 && (int) $request->user()->id_empresa !== (int) $id) {
            return $this->error('No tienes permiso para ver esta empresa', 403);
        }

        $empresa = Empresa::with(['usuarios.rol', 'proyectos.tareas'])->find($id);

        if (! $empresa) {
            return $this->error('Empresa no encontrada', 404);
        }

        return $this->success($empresa);
    }

    public function update(Request $request, string $id)
    {
        if ((int) $request->user()->id_roles !== 1 && (int) $request->user()->id_empresa !== (int) $id) {
            return $this->error('No tienes permiso para editar esta empresa', 403);
        }

        $empresa = Empresa::find($id);

        if (! $empresa) {
            return $this->error('Empresa no encontrada', 404);
        }

        $validator = Validator::make($request->all(), [
            'nombre' => ['sometimes', 'string', 'max:200'],
            'nit' => ['sometimes', 'string', 'max:30', Rule::unique('empresa', 'nit')->ignore($empresa->id_empresa, 'id_empresa')],
            'email' => ['sometimes', 'email', 'max:150', Rule::unique('empresa', 'email')->ignore($empresa->id_empresa, 'id_empresa')],
            'telefono' => ['nullable', 'string', 'max:20'],
            'direccion' => ['nullable', 'string', 'max:300'],
            'industria' => ['nullable', 'string', 'max:100'],
            'plan_suscripcion' => ['nullable', 'string', 'max:50'],
            'sector' => ['nullable', 'string', 'max:50'],
            'administrador' => ['nullable', 'string', 'max:120'],
            'num_empleados' => ['nullable', 'string', 'max:30'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $empresa->update($validator->validated());

        return $this->success($empresa, 'Empresa actualizada');
    }

    public function destroy(Request $request, string $id)
    {
        if ((int) $request->user()->id_roles !== 1) {
            return $this->error('Solo un administrador puede eliminar empresas', 403);
        }

        $deleted = Empresa::where('id_empresa', $id)->delete();

        if (! $deleted) {
            return $this->error('Empresa no encontrada', 404);
        }

        return $this->success(null, 'Empresa eliminada');
    }
}
