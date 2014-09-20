package com.alarmez.alarmez;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Fragment;
import android.content.DialogInterface;
import android.content.Intent;
import android.database.Cursor;
import android.media.RingtoneManager;
import android.os.Bundle;
import android.preference.PreferenceActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;


public class MainActivity extends Activity{
	
	Fragment currentFragment = null;
	
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        startService(new Intent(getBaseContext(), AlarmEZService.class));
        
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
        	currentFragment = new SettingsFragment();
        	// Display the fragment as the main content.
            getFragmentManager().beginTransaction()
            	.replace(android.R.id.content, currentFragment)
                .commit();
        	return true;
        }
        return super.onOptionsItemSelected(item);
    }
    
    @Override
    public void onBackPressed(){
    	if(currentFragment != null){
    		getFragmentManager().beginTransaction()
    		.detach(currentFragment)
    		.commit();
    		currentFragment = null;
    	}else{
    		super.onBackPressed();
    	}
    }
    
    public void selectRingtone(View v){

    	RingtoneManager ringtoneManager = new RingtoneManager(this);
    	ringtoneManager.setType(RingtoneManager.TYPE_ALARM);
        Cursor alarmCursor = ringtoneManager.getCursor();
        CharSequence items[] = new CharSequence[alarmCursor.getCount()];
        for(int i = 0; i < alarmCursor.getCount(); i++)
        	items[i] = ringtoneManager.getRingtone(i).getTitle(this.getApplicationContext());
        
    }
}
