<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Api\Concerns\RespondsWithJson;
use App\Http\Controllers\Controller;
use App\Models\Empresa;
use App\Models\SolicitudPago;
use App\Models\Usuario;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\Rule;
use Throwable;

class AuthController extends Controller
{
    use RespondsWithJson;

    public function login(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'email' => ['required', 'email', 'max:150'],
            'password' => ['required', 'string', 'min:8'],
            'remember' => ['sometimes', 'boolean'],
        ]);

        if ($validator->fails()) {
            return $this->error('Error de validacion', 422, $validator->errors()->toArray());
        }

        $email = strtolower(trim($request->string('email')));
        $key = 'login:'.$email.'|'.$request->ip();

        if (RateLimiter::tooManyAttempts($key, 10)) {
            $minutes = (int) ceil(RateLimiter::availableIn($key) / 60);
            return $this->error("Demasiados intentos fallidos. Espera {$minutes} minuto(s).", 429);
        }

        $usuario = Usuario::with(['empresa', 'rol'])->where('email', $email)->first();

        if (! $usuario || ! Hash::check($request->password, $usuario->password)) {
            RateLimiter::hit($key, 15 * 60);
            return $this->error('Correo o contrasena incorrectos.', 401);
        }

        if (! $usuario->estado) {
            return $this->error('Tu cuenta esta inactiva o pendiente de verificacion. Contacta a soporte.', 403);
        }

        RateLimiter::clear($key);

        if ($request->hasSession()) {
            Auth::guard('web')->login($usuario, $request->boolean('remember'));
            $request->session()->regenerate();
        }

        $tokenName = $request->boolean('remember') ? 'api-remember' : 'api';
        $token = $usuario->createToken($tokenName)->plainTextToken;

        return $this->success([
            'token' => $token,
            'token_type' => 'Bearer',
            'redirect' => '/Panel',
            'usuario' => $this->usuarioPayload($usuario),
        ], 'Bienvenido, '.$usuario->nombres.'!');
    }

    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'nombre' => ['required_without:nombre_empresa', 'string', 'max:200'],
            'nombre_empresa' => ['required_without:nombre', 'string', 'max:200'],
            'nit' => ['required', 'string', 'max:30', Rule::unique('empresa', 'nit')],
            'sector' => ['required', 'string', 'max:50'],
            'num_empleados' => ['required', 'string', 'max:30'],
            'nombres' => ['required', 'string', 'max:100'],
            'apellidos' => ['nullable', 'string', 'max:100'],
            'cargo' => ['nullable', 'string', 'max:80'],
            'email' => ['required', 'email', 'max:150', Rule::unique('usuarios', 'email'), Rule::unique('empresa', 'email')],
            'telefono' => ['required', 'string', 'max:20'],
            'password' => ['required', 'string', 'min:8', 'max:128'],
            'plan' => ['nullable', Rule::in(['starter', 'business', 'enterprise'])],
            'metodo_pago' => ['nullable', 'string', 'max:50'],
            'referencia' => ['nullable', 'string', 'max:100'],
            'notas' => ['nullable', 'string'],
            'comprobante' => ['nullable', 'file', 'mimes:pdf,png,jpg,jpeg', 'max:10240'],
        ]);

        if ($validator->fails()) {
            return $this->error('Por favor corrige los errores.', 422, $validator->errors()->toArray());
        }

        $data = $validator->validated();
        $comprobante = null;

        try {
            if ($request->hasFile('comprobante')) {
                $comprobante = $request->file('comprobante')->store('comprobantes', 'public');
            }

            $empresa = DB::transaction(function () use ($data, $comprobante) {
                $empresa = Empresa::create([
                    'nombre' => $data['nombre_empresa'] ?? $data['nombre'],
                    'nit' => $data['nit'],
                    'email' => strtolower($data['email']),
                    'telefono' => $data['telefono'],
                    'industria' => $data['sector'],
                    'plan_suscripcion' => $data['plan'] ?? 'business',
                    'sector' => $data['sector'],
                    'administrador' => trim($data['nombres'].' '.($data['apellidos'] ?? '-')),
                    'num_empleados' => $data['num_empleados'],
                    'comprobante' => $comprobante,
                    'fecha_creacion' => now(),
                ]);

                Usuario::create([
                    'nombres' => $data['nombres'],
                    'apellidos' => $data['apellidos'] ?? '-',
                    'email' => strtolower($data['email']),
                    'password' => Hash::make($data['password']),
                    'cargo' => $data['cargo'] ?? null,
                    'telefono' => $data['telefono'],
                    'id_empresa' => $empresa->id_empresa,
                    'id_roles' => 1,
                    'estado' => 1,
                    'fecha_creacion' => now(),
                ]);

                SolicitudPago::create([
                    'id_empresa' => $empresa->id_empresa,
                    'plan' => $data['plan'] ?? 'business',
                    'metodo_pago' => $data['metodo_pago'] ?? null,
                    'referencia' => $data['referencia'] ?? null,
                    'notas' => $data['notas'] ?? null,
                    'ruta_comprobante' => $comprobante,
                    'estado' => 'pendiente',
                    'fecha_creacion' => now(),
                ]);

                return $empresa;
            });

            return $this->success(['empresa_id' => $empresa->id_empresa], 'Registro completado. Tu solicitud esta en revision.', 201);
        } catch (Throwable $exception) {
            report($exception);

            return $this->error('Error al registrar la empresa. Por favor intentalo de nuevo.', 500);
        }
    }

    public function me(Request $request)
    {
        return $this->success($this->usuarioPayload($request->user()->load(['empresa', 'rol'])), 'Usuario autenticado');
    }

    public function logout(Request $request)
    {
        $token = $request->user()->currentAccessToken();
        if ($token) {
            $token->delete();
        }

        return $this->success(null, 'Sesion cerrada');
    }

    private function usuarioPayload(Usuario $usuario): array
    {
        return [
            'id_usuario' => $usuario->id_usuario,
            'nombre' => trim($usuario->nombres.' '.$usuario->apellidos),
            'nombres' => $usuario->nombres,
            'apellidos' => $usuario->apellidos,
            'email' => $usuario->email,
            'cargo' => $usuario->cargo,
            'avatar' => $usuario->avatar,
            'estado' => (bool) $usuario->estado,
            'id_empresa' => $usuario->id_empresa,
            'empresa' => $usuario->empresa?->nombre,
            'id_roles' => $usuario->id_roles,
            'rol' => $usuario->rol?->nombre ?? 'Colaborador',
        ];
    }
}
