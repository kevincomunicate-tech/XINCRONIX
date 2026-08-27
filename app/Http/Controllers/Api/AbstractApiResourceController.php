<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Http\Controllers\Controller;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

abstract class AbstractApiResourceController extends Controller
{
    use RespondsWithJson;

    protected string $model;
    protected array $storeRules = [];
    protected array $updateRules = [];
    protected ?string $companyColumn = null;
    protected ?string $userColumn = null;
    protected bool $adminOnlyWrites = false;

    public function index(Request $request)
    {
        return $this->success(
            $this->scopedQuery($request)->orderByDesc($this->primaryKey())->paginate(min($request->integer('limit', 100), 500)),
            'Registros obtenidos'
        );
    }

    public function store(Request $request)
    {
        if ($this->adminOnlyWrites && (int) $request->user()->id_roles !== 1) {
            return $this->error('No tienes permiso para crear este recurso', 403);
        }

        $validator = Validator::make($request->all(), $this->storeRules);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $data = $validator->validated();

        if ($this->companyColumn) {
            $data[$this->companyColumn] = $request->user()->id_empresa;
        }

        if ($this->userColumn && ! isset($data[$this->userColumn])) {
            $data[$this->userColumn] = $request->user()->id_usuario;
        }

        $model = $this->model::create($data);

        return $this->success($model, 'Registro creado', 201);
    }

    public function show(Request $request, string $id)
    {
        $model = $this->scopedQuery($request)->find($id);

        if (! $model) {
            return $this->error('Registro no encontrado', 404);
        }

        return $this->success($model);
    }

    public function update(Request $request, string $id)
    {
        if ($this->adminOnlyWrites && (int) $request->user()->id_roles !== 1) {
            return $this->error('No tienes permiso para editar este recurso', 403);
        }

        $model = $this->scopedQuery($request)->find($id);

        if (! $model) {
            return $this->error('Registro no encontrado', 404);
        }

        $validator = Validator::make($request->all(), $this->updateRules ?: $this->storeRules);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $model->update($validator->validated());

        return $this->success($model, 'Registro actualizado');
    }

    public function destroy(Request $request, string $id)
    {
        if ($this->adminOnlyWrites && (int) $request->user()->id_roles !== 1) {
            return $this->error('No tienes permiso para eliminar este recurso', 403);
        }

        $deleted = $this->scopedQuery($request)->where($this->primaryKey(), $id)->delete();

        if (! $deleted) {
            return $this->error('Registro no encontrado', 404);
        }

        return $this->success(null, 'Registro eliminado');
    }

    protected function scopedQuery(Request $request): Builder
    {
        $query = $this->model::query();

        if ($this->companyColumn) {
            $query->where($this->companyColumn, $request->user()->id_empresa);
        }

        if ($this->userColumn) {
            $query->where($this->userColumn, $request->user()->id_usuario);
        }

        return $query;
    }

    protected function primaryKey(): string
    {
        return (new $this->model)->getKeyName();
    }
}
