<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Models\Mensaje;
use App\Models\Usuario;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;

class MensajeController extends Controller
{
    use RespondsWithJson;

    public function index(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'con_id' => ['nullable', 'integer'],
            'desde_id' => ['nullable', 'integer', 'min:0'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        if (! $request->filled('con_id')) {
            return $this->noLeidos($request);
        }

        $contacto = Usuario::where('id_empresa', $request->user()->id_empresa)->find($request->integer('con_id'));

        if (! $contacto) {
            return $this->error('No puede chatear con este usuario', 403);
        }

        $me = $request->user()->id_usuario;
        $con = $contacto->id_usuario;

        $mensajes = Mensaje::query()
            ->where(function ($query) use ($me, $con) {
                $query->where('id_usuario', $me)->where('id_destinatario', $con);
            })
            ->orWhere(function ($query) use ($me, $con) {
                $query->where('id_usuario', $con)->where('id_destinatario', $me);
            })
            ->when($request->integer('desde_id') > 0, fn ($q) => $q->where('id_mensajes', '>', $request->integer('desde_id')))
            ->orderBy('id_mensajes')
            ->limit(200)
            ->get()
            ->map(function (Mensaje $mensaje) use ($me) {
                $mensaje->propio = (int) $mensaje->id_usuario === (int) $me;
                return $mensaje;
            });

        return $this->success($mensajes, 'Mensajes obtenidos');
    }

    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'destinatario_id' => ['required_without:id_destinatario', 'integer'],
            'id_destinatario' => ['required_without:destinatario_id', 'integer'],
            'contenido' => ['required', 'string', 'max:2000'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $destinatarioId = $request->integer('destinatario_id') ?: $request->integer('id_destinatario');

        if ((int) $destinatarioId === (int) $request->user()->id_usuario) {
            return $this->error('No puedes enviarte un mensaje a ti mismo', 400);
        }

        $destinatario = Usuario::where('id_empresa', $request->user()->id_empresa)->find($destinatarioId);

        if (! $destinatario) {
            return $this->error('No puede enviar mensajes a este usuario', 403);
        }

        $mensaje = Mensaje::create([
            'contenido' => trim($request->contenido),
            'fecha_envio' => now(),
            'estado' => true,
            'id_usuario' => $request->user()->id_usuario,
            'id_destinatario' => $destinatario->id_usuario,
        ]);

        $mensaje->propio = true;

        return $this->success($mensaje, 'Mensaje enviado', 201);
    }

    public function show(Request $request, string $id)
    {
        $mensaje = Mensaje::where(function ($query) use ($request) {
            $query->where('id_usuario', $request->user()->id_usuario)
                ->orWhere('id_destinatario', $request->user()->id_usuario);
        })->find($id);

        if (! $mensaje) {
            return $this->error('Mensaje no encontrado', 404);
        }

        return $this->success($mensaje);
    }

    public function update(Request $request, string $id)
    {
        $mensaje = Mensaje::where(function ($query) use ($request) {
            $query->where('id_usuario', $request->user()->id_usuario)
                ->orWhere('id_destinatario', $request->user()->id_usuario);
        })->find($id);

        if (! $mensaje) {
            return $this->error('Mensaje no encontrado', 404);
        }

        $validator = Validator::make($request->all(), [
            'contenido' => ['sometimes', 'string', 'max:2000'],
            'estado' => ['sometimes', 'boolean'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $mensaje->update($validator->validated());

        return $this->success($mensaje, 'Mensaje actualizado');
    }

    public function destroy(Request $request, string $id)
    {
        $deleted = Mensaje::where('id_usuario', $request->user()->id_usuario)->where('id_mensajes', $id)->delete();

        if (! $deleted) {
            return $this->error('Mensaje no encontrado', 404);
        }

        return $this->success(null, 'Mensaje eliminado');
    }

    public function equipo(Request $request)
    {
        $usuario = $request->user()->load('rol');
        $miembros = Usuario::with('rol')
            ->withCount([
                'tareas as tareas_activas' => fn ($q) => $q->where('estado', '<>', 'Completada'),
                'tareas as proyectos' => fn ($q) => $q->selectRaw('count(distinct id_proyecto)'),
            ])
            ->where('id_empresa', $usuario->id_empresa)
            ->orderBy('nombres')
            ->get()
            ->map(function (Usuario $miembro) {
                $miembro->nombre_rol = $miembro->rol?->nombre;
                $miembro->iniciales = $this->initials(trim($miembro->nombres.' '.$miembro->apellidos));
                $miembro->carga_pct = min(100, (int) $miembro->tareas_activas * 12);
                return $miembro;
            });

        return $this->success([
            'usuario' => [
                'id_usuario' => $usuario->id_usuario,
                'nombres' => $usuario->nombres,
                'apellidos' => $usuario->apellidos,
                'email' => $usuario->email,
                'cargo' => $usuario->cargo,
                'avatar' => $usuario->avatar,
                'nombre_rol' => $usuario->rol?->nombre,
                'iniciales' => $this->initials(trim($usuario->nombres.' '.$usuario->apellidos)),
            ],
            'miembros' => $miembros,
        ], 'Datos de equipo cargados');
    }

    public function noLeidos(Request $request)
    {
        $resultado = Mensaje::selectRaw('id_usuario AS remitente_id, COUNT(*) AS cantidad')
            ->where('id_destinatario', $request->user()->id_usuario)
            ->where('estado', true)
            ->groupBy('id_usuario')
            ->with(['remitente' => fn ($q) => $q->select('id_usuario', 'nombres', 'apellidos', 'avatar')])
            ->get();

        return $this->success($resultado, 'Mensajes sin leer obtenidos');
    }

    private function initials(string $name): string
    {
        $initials = collect(explode(' ', trim($name)))
            ->filter()
            ->map(fn ($part) => mb_strtoupper(mb_substr($part, 0, 1)))
            ->implode('');

        return mb_substr($initials, 0, 2) ?: 'SA';
    }
}
