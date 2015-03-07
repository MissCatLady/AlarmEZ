package com.alarmez.alarmez;

import java.io.IOException;
import java.util.Timer;
import java.util.TimerTask;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Binder;
import android.os.Handler;
import android.os.IBinder;
import android.preference.PreferenceManager;
import android.support.v4.app.NotificationCompat;

/**
 * Background service to check for and run alarms.
 */
public class AlarmEZService extends Service {

    public class AlarmEZBinder extends Binder {
        AlarmEZService getService(){
            return AlarmEZService.this;
        }
    }
    private final IBinder mBinder = new AlarmEZBinder();

    //Timer interval length.
    private static int ALARM_TIMER = 5000;

    //Timer to run alarm check every ALARM_TIMER milliseconds.
	private Timer mTimer = null;
	private Handler mHandler = new Handler();

    //Ringtone Manager to load ringtones.
	RingtoneManager ringtoneManager = new RingtoneManager(this);
	NotificationCompat.Builder mBuilder = new NotificationCompat.Builder(this);

    //MediaPlayer that plats alarm.
	public static MediaPlayer mediaPlayer;
	
	class TimeDisplayTimerTask extends TimerTask {
		public AlarmEZService host;
		
		TimeDisplayTimerTask(Service h){
			host = (AlarmEZService)h;
		}
		
        @Override
        public void run() {

            //TODO: Check server for alarms.
            //Run alarm if any alarms activated.

            // run on another thread
            mHandler.post(new Runnable() {
 
                @Override
                public void run() {
            		host.playAlarm();
                }
 
            });
        }
 
    }

    /**
     * Creates an alarm notification and plays alarm.
     */
	public void playAlarm(){
		//Create notification.
    	mBuilder.setSmallIcon(R.drawable.ic_launcher)
                .setContentTitle("Alarm from ___")
                .setContentText("WAKE UP")
                .setAutoCancel(true)
                .setDefaults(Notification.DEFAULT_LIGHTS | Notification.FLAG_AUTO_CANCEL);

    	PendingIntent i = PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), 0);
    	mBuilder.setContentIntent(i);
                
        // Creates an explicit intent for an Activity in your app
        
        NotificationManager mNotificationManager =
            (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        
        // mId allows you to update the notification later on.
        int mId = 0;
        mNotificationManager.notify(mId, mBuilder.build());
		
        //Play alarm.
        SharedPreferences sharedPrefs = PreferenceManager.getDefaultSharedPreferences(getApplicationContext());
        AudioManager audio = (AudioManager)getApplicationContext().getSystemService(Context.AUDIO_SERVICE);
        int max = audio.getStreamMaxVolume(AudioManager.STREAM_NOTIFICATION);
        int user_vol = sharedPrefs.getInt("alarm_volume", 100);
        int vol = (int)(((float)max)*((float)user_vol/100.0f));
        System.out.println("Vol: " + vol + "/" + max);
        audio.setRingerMode(AudioManager.RINGER_MODE_NORMAL);
        audio.setStreamVolume(AudioManager.STREAM_RING, vol, AudioManager.FLAG_REMOVE_SOUND_AND_VIBRATE);
        
        ringtoneManager.setStopPreviousRingtone(true);
        ringtoneManager.setType(RingtoneManager.TYPE_ALARM);
        
        
        String ringtone = sharedPrefs.getString("alarm_ringtone", "");
        System.out.println(ringtone);

        
        Uri ringtoneUri = Uri.parse(ringtone);
        
        if(mediaPlayer != null)
        	mediaPlayer.reset();
        
        try{
        	mediaPlayer.setLooping(true);
        	mediaPlayer.setAudioStreamType(AudioManager.STREAM_RING);
	        mediaPlayer.setDataSource(getApplicationContext(), ringtoneUri);
	        mediaPlayer.prepare();
	        mediaPlayer.start();
        }
        catch(Exception ex){
        	
        	System.out.println("Failing: " + ex.getMessage());
        }
        System.out.println("Alarm launched");
	}

    /**
     * Stop alarm sound from playing.
     */
    public void stopAlarm(){
        System.out.println("Stopping alarm");
        if(mediaPlayer != null){
            mediaPlayer.stop();
        }
    }
	
	@Override
	public void onCreate() {
		super.onCreate();
	}
	
	@Override
	public void onDestroy(){
        System.out.println("Service being destroyed.");
		if(mediaPlayer != null){
            mediaPlayer.stop();
			mediaPlayer.reset();
		}
	}
	
	@Override
	public int onStartCommand(Intent intent, int flags, int startId) {
		
		if(mTimer != null) {
            mTimer.cancel();
            mTimer = new Timer();
        } else {
            // recreate new
            mTimer = new Timer();
        }

        //Schedule task every ALARM_TIMER
        mTimer.scheduleAtFixedRate(new TimeDisplayTimerTask(this), ALARM_TIMER, ALARM_TIMER);
        super.onStartCommand(intent, flags, startId);

        if(mediaPlayer == null)
            mediaPlayer = new MediaPlayer();
		return START_STICKY;
	}

	@Override
	public IBinder onBind(Intent intent) {
        return mBinder;
	}
}